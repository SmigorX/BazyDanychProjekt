from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

# Tabela udostępniania notatek konkretnym userom (WB.3)
class NoteShare(Base):
    __tablename__ = "note_shares"
    note_id = Column(UUID(as_uuid=True), ForeignKey("notes.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    can_edit = Column(Boolean, default=False) 

class Password(Base):
    __tablename__ = "passwords"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    algorithm = Column(String, nullable=False)
    # PRZYWRÓCONA LINIJKA PONIŻEJ:
    number_of_passes = Column(Integer, default=12) 
    
    user = relationship("User", back_populates="password", uselist=False)

class GroupMember(Base):
    __tablename__ = "group_members"
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role = Column(String, default="member") 
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="groups")
    group = relationship("Group", back_populates="members")

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    description = Column(String, nullable=True)
    profile_picture_url = Column(String, nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    password_id = Column(UUID(as_uuid=True), ForeignKey("passwords.id"))
    
    password = relationship("Password", back_populates="user")
    notes = relationship("Note", back_populates="owner") 
    groups = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    shared_notes = relationship("Note", secondary="note_shares", backref="shared_with_users")

class Group(Base):
    __tablename__ = "groups"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="group")

class Note(Base):
    __tablename__ = "notes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True)
    content = Column(String)
    color = Column(String, default="#FFFFFF")
    latitude = Column(Float)
    longitude = Column(Float)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=True)
    
    owner = relationship("User", back_populates="notes")
    group = relationship("Group", back_populates="notes")