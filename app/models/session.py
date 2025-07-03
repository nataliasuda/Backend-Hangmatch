from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

session_user_association = Table(
    'session_user',
    Base.metadata,
    Column('session_id', Integer, ForeignKey('sessions.id')),
    Column('user_id', Integer, ForeignKey('users.id')))

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location_radius = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="owned_sessions")
    invited_users = relationship("User", secondary=session_user_association, back_populates="invited_sessions")