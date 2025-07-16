from sqlalchemy import Column, Integer, ForeignKey, Enum, String
from app.database import Base
from sqlalchemy.orm import relationship
import enum
import uuid

class FriendRequestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class FriendRequest(Base):
    __tablename__ = "friend_requests"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(String, ForeignKey("users.id"), default=lambda: str(uuid.uuid4()))
    receiver_id = Column(String, ForeignKey("users.id"), default=lambda: str(uuid.uuid4()))
    status = Column(Enum(FriendRequestStatus), default=FriendRequestStatus.pending)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_friend_requests")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_friend_requests")
