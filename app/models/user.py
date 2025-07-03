from sqlalchemy import Column, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    sent_friend_requests = relationship("FriendRequest", back_populates="sender", foreign_keys='FriendRequest.sender_id')
    received_friend_requests = relationship("FriendRequest", back_populates="receiver", foreign_keys='FriendRequest.receiver_id')
