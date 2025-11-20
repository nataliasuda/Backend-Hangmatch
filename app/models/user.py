from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    invited_sessions = relationship("Session", secondary="session_user", back_populates="invited_users", viewonly=True)
    owned_sessions = relationship("Session", back_populates="owner")
    invited_users_association = relationship("SessionUser", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
   
    sent_friend_requests = relationship("FriendRequest", back_populates="sender", foreign_keys='FriendRequest.sender_id')
    received_friend_requests = relationship("FriendRequest", back_populates="receiver", foreign_keys='FriendRequest.receiver_id')
    