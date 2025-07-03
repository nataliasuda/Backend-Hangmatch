from sqlalchemy import Column, Integer, ForeignKey, Enum
from app.database import Base
from sqlalchemy.orm import relationship
import enum

class FriendRequestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class FriendRequest(Base):
    __tablename__ = "friend_requests"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(FriendRequestStatus), default=FriendRequestStatus.pending)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_friend_requests")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_friend_requests")
