from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
import uuid, enum

class SessionRequestStatus(str, enum.Enum):
    invited = "invited"
    accepted = "accepted"
    rejected = "rejected"
    

class SessionUser(Base):
    __tablename__ = "session_user"
    session_id = Column(String, ForeignKey('sessions.id', ondelete="CASCADE"), primary_key=True)
    user_id = Column(String, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    status = Column(String, default='invited')

    session = relationship("Session", back_populates="invited_users_association")
    user = relationship("User", back_populates="invited_users_association")


class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    location_radius = Column(Integer, nullable=False)
    owner_id = Column(String, ForeignKey('users.id'), default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default='draft')  

    owner = relationship("User", back_populates="owned_sessions")
    invited_users_association = relationship("SessionUser", back_populates="session", cascade="all, delete-orphan", passive_deletes=True)
    invited_users = relationship("User", secondary="session_user", back_populates="invited_sessions", viewonly=True)