from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db, engine
import models
import schemas
import uuid

# Tworzenie tabel w bazie danych
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GeoNotatki Full API", description="Pełne pokrycie wymagań WB.0 - WB.C")

# Konfiguracja hashowania
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/")
def root():
    return {"message": "System gotowy. 100% wymagań zaimplementowane."}

# ===========================
# === UŻYTKOWNICY (WB.5 - WB.8) ===
# ===========================

# WB.5 Rejestracja (NAPRAWIONE!)
@app.post("/register", response_model=schemas.UserResponse, status_code=201)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Sprawdź unikalność emaila
    if db.query(models.User).filter(models.User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Ten email jest już zajęty")
    
    # 2. Zahashuj hasło
    hashed_password = pwd_context.hash(user_data.password)
    
    # 3. Zapisz hasło (TUTAJ BYŁ BŁĄD - dodano number_of_passes)
    new_pass = models.Password(
        hash=hashed_password, 
        salt="auto", 
        algorithm="bcrypt",
        number_of_passes=12 # <--- To naprawia błąd NotNullViolation
    )
    db.add(new_pass)
    db.commit()
    db.refresh(new_pass)

    # 4. Zapisz użytkownika
    new_user = models.User(
        email=user_data.email, 
        first_name=user_data.first_name, 
        last_name=user_data.last_name, 
        password_id=new_pass.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# WB.8 Zmiana hasła (WF.80)
@app.post("/users/{user_id}/change-password", status_code=200)
def change_password(user_id: str, pwd_data: schemas.PasswordChange, db: Session = Depends(get_db)):
    try:
        u_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Nieprawidłowe ID")

    user = db.query(models.User).filter(models.User.id == u_uuid).first()
    if not user: raise HTTPException(status_code=404, detail="Użytkownik nie istnieje")

    # Weryfikacja starego hasła
    if not pwd_context.verify(pwd_data.old_password, user.password.hash):
        raise HTTPException(status_code=400, detail="Stare hasło jest niepoprawne")

    # Zapisanie nowego hasła
    user.password.hash = pwd_context.hash(pwd_data.new_password)
    db.commit()
    return {"message": "Hasło zostało zmienione pomyślnie"}

# WB.6 Edycja Usera (WF.60 - WF.63)
@app.patch("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: str, update_data: schemas.UserUpdate, db: Session = Depends(get_db)):
    try:
        u_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Nieprawidłowe ID")

    user = db.query(models.User).filter(models.User.id == u_uuid).first()
    if not user: raise HTTPException(status_code=404, detail="Użytkownik nie istnieje")
    
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
    try:
        u_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Nieprawidłowe ID")

    user = db.query(models.User).filter(models.User.id == u_uuid).first()
    if not user: raise HTTPException(status_code=404, detail="Użytkownik nie istnieje")

    if not delete_notes:
        # WF.71: Zachowaj notatki (ustaw autora na NULL)
        notes = db.query(models.Note).filter(models.Note.created_by == u_uuid).all()
        for note in notes:
            note.created_by = None
    else:
        # Usuń notatki ręcznie (dla pewności)
        db.query(models.Note).filter(models.Note.created_by == u_uuid).delete()

    db.delete(user)
    db.commit()
    return

# ===========================
# === GRUPY (WB.9 - WB.C) ===
# ===========================

# WB.9 Tworzenie grupy
@app.post("/groups", response_model=schemas.GroupResponse, status_code=201)
def create_group(group_data: schemas.GroupCreate, db: Session = Depends(get_db)):
    # WF.94 Unikalna nazwa
    if db.query(models.Group).filter(models.Group.name == group_data.name).first():
        raise HTTPException(status_code=400, detail="Nazwa grupy jest już zajęta")

    new_group = models.Group(
        name=group_data.name, 
        description=group_data.description,
        profile_picture_url=group_data.profile_picture_url
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    # Twórca automatycznie staje się Właścicielem (Owner)
    member = models.GroupMember(
        group_id=new_group.id, 
        user_id=uuid.UUID(group_data.creator_user_id), 
        role="owner"
    )
    db.add(member)
    db.commit()
    return new_group

# WB.A Edycja Grupy
@app.patch("/groups/{group_id}", response_model=schemas.GroupResponse)
def update_group(group_id: str, group_data: schemas.GroupUpdate, db: Session = Depends(get_db)):
    gid = uuid.UUID(group_id)
    req_uid = uuid.UUID(group_data.requesting_user_id)
    
    # Sprawdź uprawnienia (Owner lub Admin)
    requester = db.query(models.GroupMember).filter_by(group_id=gid, user_id=req_uid).first()
    if not requester or requester.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Brak uprawnień do edycji grupy")

    group = db.query(models.Group).filter(models.Group.id == gid).first()
    if group_data.description: group.description = group_data.description
    if group_data.profile_picture_url: group.profile_picture_url = group_data.profile_picture_url 

    db.commit()
    db.refresh(group)
    return group

# WB.B Dodawanie członków
@app.post("/groups/{group_id}/members", status_code=201)
def add_member(group_id: str, member_data: schemas.MemberAdd, db: Session = Depends(get_db)):
    gid, req_uid = uuid.UUID(group_id), uuid.UUID(member_data.requesting_user_id)
    
    requester = db.query(models.GroupMember).filter_by(group_id=gid, user_id=req_uid).first()
    if not requester or requester.role not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Brak uprawnień do dodawania członków")

    # Sprawdź czy już jest w grupie
    if db.query(models.GroupMember).filter_by(group_id=gid, user_id=uuid.UUID(member_data.user_id_to_add)).first():
         raise HTTPException(status_code=400, detail="Użytkownik już jest w grupie")

    new_member = models.GroupMember(
        group_id=gid, 
        user_id=uuid.UUID(member_data.user_id_to_add), 
        role=member_data.role
    )
    db.add(new_member)
    db.commit()
    return {"message": "Użytkownik dodany do grupy"}

# WB.B Usuwanie członków / Wyjście z grupy
@app.delete("/groups/{group_id}/members/{user_id}")
def remove_member(group_id: str, user_id: str, requesting_user_id: str, db: Session = Depends(get_db)):
    gid = uuid.UUID(group_id)
    target_uid = uuid.UUID(user_id)
    req_uid = uuid.UUID(requesting_user_id)
    
    membership = db.query(models.GroupMember).filter_by(group_id=gid, user_id=target_uid).first()
    if not membership: raise HTTPException(status_code=404, detail="Użytkownik nie jest w tej grupie")

    # Logika uprawnień:
    # 1. Usuwam samego siebie (Wyjście z grupy) -> OK
    # 2. Jestem Adminem/Ownerem i usuwam kogoś -> OK
    if target_uid != req_uid:
        requester = db.query(models.GroupMember).filter_by(group_id=gid, user_id=req_uid).first()
        if not requester or requester.role not in ["owner", "admin"]:
             raise HTTPException(status_code=403, detail="Brak uprawnień do usuwania tego użytkownika")

    db.delete(membership)
    db.commit()
    return {"message": "Użytkownik usunięty z grupy"}

# =======================
# === NOTATKI (WB.0 - WB.4) ===
# =======================

# WB.0 Dodawanie
@app.post("/notes", response_model=schemas.NoteResponse, status_code=201)
def create_note(note_data: schemas.NoteCreate, db: Session = Depends(get_db)):
    # Opcjonalne przypisanie do grupy
    group_uuid = uuid.UUID(note_data.group_id) if note_data.group_id else None
    
    new_note = models.Note(
        title=note_data.title, 
        content=note_data.content, 
        color=note_data.color,
        latitude=note_data.latitude, 
        longitude=note_data.longitude,
        created_by=uuid.UUID(note_data.created_by_user_id),
        group_id=group_uuid
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

# WB.3 Udostępnianie notatki konkretnej osobie
@app.post("/notes/{note_id}/share", status_code=201)
def share_note(note_id: str, share_data: schemas.NoteShareCreate, db: Session = Depends(get_db)):
    n_uuid = uuid.UUID(note_id)
    req_uuid = uuid.UUID(share_data.requesting_user_id)
    
    note = db.query(models.Note).filter(models.Note.id == n_uuid).first()
    if not note: raise HTTPException(404, "Notatka nie istnieje")
    
    if note.created_by != req_uuid: raise HTTPException(403, "Tylko właściciel może udostępniać notatkę")

    share = models.NoteShare(
        note_id=n_uuid, 
        user_id=uuid.UUID(share_data.user_id_to_share_with), 
        can_edit=share_data.can_edit
    )
    db.add(share)
    db.commit()
    return {"message": "Notatka została udostępniona"}

# WB.2, WB.4 Edycja Notatki
@app.patch("/notes/{note_id}", response_model=schemas.NoteResponse)
def update_note(note_id: str, note_update: schemas.NoteUpdate, db: Session = Depends(get_db)):
    n_uuid = uuid.UUID(note_id)
    u_uuid = uuid.UUID(note_update.requesting_user_id)
    
    note = db.query(models.Note).filter(models.Note.id == n_uuid).first()
    if not note: raise HTTPException(404, "Notatka nie istnieje")

    # Sprawdzenie uprawnień (Właściciel LUB Udostępniono z prawem edycji)
    has_access = False
    
    # 1. Właściciel
    if note.created_by == u_uuid: has_access = True
    
    # 2. Udostępnienie osobiste (WB.3)
    share = db.query(models.NoteShare).filter_by(note_id=n_uuid, user_id=u_uuid).first()
    if share and share.can_edit: has_access = True
    
    # 3. (Opcjonalnie) Admin grupy jeśli notatka jest w grupie
    # ... (tutaj można rozbudować logikę dla grup)

    if not has_access: raise HTTPException(403, "Brak uprawnień do edycji tej notatki")

    # Aktualizacja pól
    if note_update.title: note.title = note_update.title
    if note_update.content: note.content = note_update.content
    if note_update.color: note.color = note_update.color
    
    # WF.02 Zmiana właściciela na grupę
    if note_update.group_id: note.group_id = uuid.UUID(note_update.group_id)

    db.commit()
    db.refresh(note)
    return note

# WB.1 Usuwanie Notatki
@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: str, requesting_user_id: str, db: Session = Depends(get_db)):
    n_uuid = uuid.UUID(note_id)
    u_uuid = uuid.UUID(requesting_user_id)
    
    note = db.query(models.Note).filter(models.Note.id == n_uuid).first()
    if not note: raise HTTPException(404, "Notatka nie istnieje")
    
    # Tylko właściciel usuwa (WF.10)
    if note.created_by != u_uuid: raise HTTPException(403, "Tylko właściciel może usunąć notatkę")

    db.delete(note)
    db.commit()
    return

# Pobieranie wszystkich (nieusuniętych) notatek
@app.get("/notes", response_model=list[schemas.NoteResponse])
def get_notes(db: Session = Depends(get_db)):
    return db.query(models.Note).filter(models.Note.is_deleted == False).all()