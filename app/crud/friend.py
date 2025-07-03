from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import FriendRequest, FriendRequestStatus, User

def send_friend_request(db: Session, sender_id: int, receiver_email: str):
    receiver = db.query(User).filter(User.email == receiver_email).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(FriendRequest).filter(
        FriendRequest.sender_id == sender_id,
        FriendRequest.receiver_id == receiver.id,
        FriendRequest.status == FriendRequestStatus.pending
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Friend request already sent")

    friend_request = FriendRequest(
        sender_id=sender_id,
        receiver_id=receiver.id,
        status=FriendRequestStatus.pending
    )
    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)
    return friend_request

def respond_to_request(db: Session, request_id: int, accept: bool):
    request = db.query(FriendRequest).filter(FriendRequest.id == request_id).first()
    if not request or request.status != FriendRequestStatus.pending:
        raise HTTPException(status_code=404, detail="Request not found or already handled")

    request.status = FriendRequestStatus.accepted if accept else FriendRequestStatus.rejected
    db.commit()
    db.refresh(request)
    return request

def delete_friendship(db: Session, user1_id: int, user2_id: int):
    request = db.query(FriendRequest).filter(
        ((FriendRequest.sender_id == user1_id) & (FriendRequest.receiver_id == user2_id)) |
        ((FriendRequest.sender_id == user2_id) & (FriendRequest.receiver_id == user1_id)),
        FriendRequest.status == FriendRequestStatus.accepted
    ).first()

    if not request:
        raise HTTPException(status_code=404, detail="Friendship not found")

    db.delete(request)
    db.commit()
    return {"detail": "Friendship removed"}