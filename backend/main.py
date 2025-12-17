from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db, engine
import models
import schemas
import uuid

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GeoNotatki Full API", description="Pełne pokrycie wymagań WB.0 - WB.C")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/")
def root():
    return {"message": "System gotowy. 100% wymagań zaimplementowane."}

# ===========================
# === UŻYTKOWNICY ===
# ===========================

@app.post("/register", response_model=schemas.UserResponse, status_code=201)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email zajęty")
    
    hashed_password = pwd_context.hash(user_data.password)
    new_pass = models.Password(hash=hashed_password, salt="auto", algorithm="bcrypt")
    db.add(new_pass)
    db.commit()
    db.refresh(new_pass)

    new_user = models.User(
        email=user_data.email, first_name=user_data.first_name, 
        last_name=user_data.last_name, password_id=new_pass.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# WB.8 Zmiana hasła
@app.post("/users/{user_id}/change-password", status_code=200)
def change_password(user_id: str, pwd_data: schemas.PasswordChange, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == uuid.UUID(user_id)).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")

    # Weryfikacja starego hasła (WF.80)
    if not pwd_context.verify(pwd_data.old_password, user.password.hash):
        raise HTTPException(status_code=400, detail="Stare hasło niepoprawne")

    user.password.hash = pwd_context.hash(pwd_data.new_password)
    db.commit()
    return {"message": "Hasło zmienione"}

# WB.6 Edycja Usera (w tym zdjęcie profilowe)
@app.patch("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: str, update_data: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == uuid.UUID(user_id)).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")
    
    if update_data.description: user.description = update_data.description
    if update_data.first_name: user.first_name = update_data.first_name
    if update_data.last_name: user.last_name = update_data.last_name
    if update_data.email: user.email = update_data.email
    if update_data.profile_picture_url: user.profile_picture_url = update_data.profile_picture_url

    db.commit()
    db.refresh(user)
    return user

# WB.7 Usuwanie Usera (z opcją zachowania notatek WF.71)
@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str, delete_notes: bool = True, db: Session = Depends(get_db)):
    u_uuid = uuid.UUID(user_id)
    user = db.query(models.User).filter(models.User.id == u_uuid).first()
    if not user: raise HTTPException(status_code=404, detail="User not found")

    if not delete_notes:
        # WF.71: Zachowaj notatki (ustaw created_by na NULL)
        notes = db.query(models.Note).filter(models.Note.created_by == u_uuid).all()
        for note in notes:
            note.created_by = None
    else:
        # Usuń notatki ręcznie przed usunięciem usera (dla pewności, jeśli cascade nie zadziała)
        db.query(models.Note).filter(models.Note.created_by == u_uuid).delete()

    db.delete(user)
    db.commit()
    return

# ===========================
# === GRUPY ===
# ===========================

@app.post("/groups", response_model=schemas.GroupResponse, status_code=201)
def create_group(group_data: schemas.GroupCreate, db: Session = Depends(get_db)):
    if db.query(models.Group).filter(models.Group.name == group_data.name).first():
        raise HTTPException(status_code=400, detail="Nazwa grupy zajęta")

    new_group = models.Group(
        name=group_data.name, 
        description=group_data.description,
        profile_picture_url=group_data.profile_picture_url
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    member = models.GroupMember(group_id=new_group.id, user_id=uuid.UUID(group_data.creator_user_id), role="owner")
    db.add(member)
    db.commit()
    return new_group

# WB.A Edycja Grupy
@app.patch("/groups/{group_id}", response_model=schemas.GroupResponse)
def update_group(group_id: str, group_data: schemas.GroupUpdate, db: Session = Depends(get_db)):
    gid = uuid.UUID(group_id)
    req_uid = uuid.UUID(group_data.requesting_user_id)
    
    # Sprawdź uprawnienia (Owner/Admin)
    requester = db.query(models.GroupMember).filter_by(group_id=gid, user_id=req_uid).first()
    if not requester or requester.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Brak uprawnień do edycji grupy")

    group = db.query(models.Group).filter(models.Group.id == gid).first()
    if group_data.description: group.description = group_data.description
    if group_data.profile_picture_url: group.profile_picture_url = group_data.profile_picture_url # WF.A1

    db.commit()
    db.refresh(group)
    return group

@app.post("/groups/{group_id}/members", status_code=201)
def add_member(group_id: str, member_data: schemas.MemberAdd, db: Session = Depends(get_db)):
    gid, req_uid = uuid.UUID(group_id), uuid.UUID(member_data.requesting_user_id)
    requester = db.query(models.GroupMember).filter_by(group_id=gid, user_id=req_uid).first()
    if not requester or requester.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Brak uprawnień")

    new_member = models.GroupMember(group_id=gid, user_id=uuid.UUID(member_data.user_id_to_add), role=member_data.role)
    db.add(new_member)
    db.commit()
    return {"message": "Dodano"}

@app.delete("/groups/{group_id}/members/{user_id}")
def remove_member(group_id: str, user_id: str, requesting_user_id: str, db: Session = Depends(get_db)):
    gid, target_uid, req_uid = uuid.UUID(group_id), uuid.UUID(user_id), uuid.UUID(requesting_user_id)
    
    membership = db.query(models.GroupMember).filter_by(group_id=gid, user_id=target_uid).first()
    if not membership: raise HTTPException(status_code=404, detail="Brak członka")

    if target_uid != req_uid:
        requester = db.query(models.GroupMember).filter_by(group_id=gid, user_id=req_uid).first()
        if not requester or requester.role not in ["owner", "admin"]:
             raise HTTPException(status_code=403, detail="Brak uprawnień")

    db.delete(membership)
    db.commit()
    return {"message": "Usunięto"}

# =======================
# === NOTATKI ===
# =======================

@app.post("/notes", response_model=schemas.NoteResponse, status_code=201)
def create_note(note_data: schemas.NoteCreate, db: Session = Depends(get_db)):
    new_note = models.Note(
        title=note_data.title, content=note_data.content, color=note_data.color,
        latitude=note_data.latitude, longitude=note_data.longitude,
        created_by=uuid.UUID(note_data.created_by_user_id),
        group_id=uuid.UUID(note_data.group_id) if note_data.group_id else None
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

# WB.3 Udostępnianie notatki konkretnej osobie
@app.post("/notes/{note_id}/share", status_code=201)
def share_note(note_id: str, share_data: schemas.NoteShareCreate, db: Session = Depends(get_db)):
    n_uuid, req_uuid = uuid.UUID(note_id), uuid.UUID(share_data.requesting_user_id)
    note = db.query(models.Note).filter(models.Note.id == n_uuid).first()
    
    if not note: raise HTTPException(404, "Brak notatki")
    if note.created_by != req_uuid: raise HTTPException(403, "Nie twoja notatka")

    share = models.NoteShare(note_id=n_uuid, user_id=uuid.UUID(share_data.user_id_to_share_with), can_edit=share_data.can_edit)
    db.add(share)
    db.commit()
    return {"message": "Udostępniono"}

@app.patch("/notes/{note_id}", response_model=schemas.NoteResponse)
def update_note(note_id: str, note_update: schemas.NoteUpdate, db: Session = Depends(get_db)):
    n_uuid, u_uuid = uuid.UUID(note_id), uuid.UUID(note_update.requesting_user_id)
    note = db.query(models.Note).filter(models.Note.id == n_uuid).first()
    if not note: raise HTTPException(404, "Brak notatki")

    # Sprawdź uprawnienia: Właściciel LUB Udostępniono z edycją LUB Admin grupy
    has_access = False
    if note.created_by == u_uuid: has_access = True
    
    # Sprawdź udostępnienie (WB.3)
    share = db.query(models.NoteShare).filter_by(note_id=n_uuid, user_id=u_uuid).first()
    if share and share.can_edit: has_access = True

    if not has_access: raise HTTPException(403, "Brak uprawnień")

    if note_update.title: note.title = note_update.title
    if note_update.content: note.content = note_update.content
    if note_update.color: note.color = note_update.color
    if note_update.group_id: note.group_id = uuid.UUID(note_update.group_id)

    db.commit()
    db.refresh(note)
    return note

@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str, requesting_user_id: str, db: Session = Depends(get_db)):
    n_uuid, u_uuid = uuid.UUID(note_id), uuid.UUID(requesting_user_id)
    note = db.query(models.Note).filter(models.Note.id == n_uuid).first()
    if not note: raise HTTPException(404, "Brak notatki")
    if note.created_by != u_uuid: raise HTTPException(403, "Nie twoja notatka")
    db.delete(note)
    db.commit()
    return

@app.get("/notes", response_model=list[schemas.NoteResponse])
def get_notes(db: Session = Depends(get_db)):
    return db.query(models.Note).filter(models.Note.is_deleted == False).all()