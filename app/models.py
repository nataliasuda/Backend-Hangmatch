from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

session_user_association = Table(
    'session_user',
    Base.metadata,
    Column('session_id', Integer, ForeignKey('sessions.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    invited_sessions = relationship("Session", secondary=session_user_association, back_populates="invited_users")
    owned_sessions = relationship("Session", back_populates="owner")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location_radius = Column(Integer, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="owned_sessions")
    invited_users = relationship("User", secondary=session_user_association, back_populates="invited_sessions")