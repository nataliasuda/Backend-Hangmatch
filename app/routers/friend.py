from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud
from app import schemas
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import FriendRequestResponse, FriendRequestCreate, UserResponse, FriendSearchResult
from app.models import User, FriendRequest, FriendRequestStatus

router = APIRouter()

@router.post("/invite", response_model=schemas.Message)
def send_request(
    friend_request: FriendRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = crud.send_friend_request(db, current_user.id, friend_request.receiver_email)

    if not result:
        raise HTTPException(status_code=400, detail="Cannot send friend request.")
    
    return {"message": "Invite sent"}
    

@router.post("/friends/respond/{request_id}", response_model=FriendRequestResponse)
def respond_to_friend(
    request_id: str,
    accept: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = crud.respond_to_request(db, request_id, accept)

    if not result:
        raise HTTPException(status_code=404, detail="Friend request not found or already handled.")

    return result

@router.delete("/friends/remove/{user_id}", response_model=schemas.Message)
def remove_friend(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = crud.delete_friendship(db, current_user.id, user_id)

    if not success:
        raise HTTPException(status_code=404, detail="Friendship not found.")

    return {"message": "Friendship removed."}

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


@router.get("/friends/search", response_model=List[FriendSearchResult])
def search_users(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    users = db.query(User).filter(
        User.email.ilike(f"%{query}%"),
        User.id != current_user.id,
    ).all()

    results = []
    for user in users:
        friend_request = db.query(FriendRequest).filter(
            ((FriendRequest.sender_id == current_user.id) & (FriendRequest.receiver_id == user.id)) |
            ((FriendRequest.sender_id == user.id) & (FriendRequest.receiver_id == current_user.id))
        ).first()

        if not friend_request:
            status = "not_friends"
        elif friend_request.status == "pending":
            status = "pending"
        elif friend_request.status == "accepted":
            status = "friends"
        else:
            status = "not_friends"

        results.append(FriendSearchResult(email=user.email, status=status))

    return results
