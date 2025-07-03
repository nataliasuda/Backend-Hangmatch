from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import FriendRequestResponse, FriendRequestCreate, UserResponse
from app.models import User, FriendRequest, FriendRequestStatus

router = APIRouter()

@router.post("/invite", response_model=FriendRequestResponse)
def send_request(
    friend_request: FriendRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.send_friend_request(db, current_user.id, friend_request.receiver_email)
    

@router.post("/friends/respond/{request_id}", response_model=FriendRequestResponse)
def respond_to_friend(
    request_id: int,
    accept: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.respond_to_request(db, request_id, accept)

@router.delete("/friends/remove/{user_id}")
def remove_friend(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.delete_friendship(db, current_user.id, user_id)

@router.get("/friends", response_model=List[UserResponse])
def get_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    accepted = db.query(FriendRequest).filter(
        ((FriendRequest.sender_id == current_user.id) | (FriendRequest.receiver_id == current_user.id)),
        FriendRequest.status == FriendRequestStatus.accepted
    ).all()

    friend_ids = [
        r.receiver_id if r.sender_id == current_user.id else r.sender_id
        for r in accepted
    ]

    return db.query(User).filter(User.id.in_(friend_ids)).all()

@router.get("/friends/requests", response_model=List[FriendRequestResponse])
def get_my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(FriendRequest).filter(
        (FriendRequest.receiver_id == current_user.id) |
        (FriendRequest.sender_id == current_user.id)
    ).all()
