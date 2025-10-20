from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Enum as SAEnum, Text, Boolean, ForeignKey, DateTime
import enum

Base = declarative_base()


class NoteCategory(enum.Enum):
    PERSONAL = "PERSONAL"
    WORK = "WORK"
    STUDY = "STUDY"
    IDEA = "IDEA"
    MEETING = "MEETING"
    OTHER = "OTHER"


class NoteDB(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(SAEnum(NoteCategory, name="notecategory"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tags = Column(Text, nullable=True)
    is_pinned = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255))


