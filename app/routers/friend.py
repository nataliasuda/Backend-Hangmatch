from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud
from app import schemas
from app.database import get_db
from app.dependencies import get_current_user
from app.schemas import FriendRequestResponse, FriendRequestCreate, UserResponse, FriendSearchResult
from app.models import User, FriendRequest, FriendRequestStatus
from app.schemas.friend import FriendRespond

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
    data: FriendRespond,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_request = crud.respond_to_request(db, request_id, data.accept)

    if not updated_request:
        raise HTTPException(status_code=404, detail="Friend request not found")


    return FriendRequestResponse(
        id=str(updated_request.id),
        sender_id=str(updated_request.sender_id),
        receiver_id=str(updated_request.receiver_id),
        status=updated_request.status.value,
        sender_email=updated_request.sender.email,
        receiver_email=updated_request.receiver.email,
        sender_name=updated_request.sender.name,
        receiver_name=updated_request.receiver.name,
        direction="incoming" if updated_request.receiver_id == current_user.id else "outgoing",
        other_email=updated_request.sender.email if updated_request.receiver_id == current_user.id else updated_request.receiver.email,
        other_name=updated_request.sender.name if updated_request.receiver_id == current_user.id else updated_request.receiver.name,
    )


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

    requests = db.query(FriendRequest).filter(
        FriendRequest.receiver_id == current_user.id, 
        FriendRequest.status == FriendRequestStatus.pending
    ).all()

    results = []
    for r in requests:
        sender_email = r.sender.email if r.sender else None
        receiver_email = r.receiver.email if r.receiver else None
        sender_name = r.sender.name if r.sender else None
        receiver_name = r.receiver.name if r.receiver else None

        results.append({
            "id": r.id,
            "sender_id": r.sender_id,
            "receiver_id": r.receiver_id,
            "status": r.status.value if hasattr(r.status, "value") else r.status,
            "sender_email": sender_email,
            "receiver_email": receiver_email,
            "direction": "incoming", 
            "other_email": sender_email,  
            "other_name": sender_name,   
            "sender_name": sender_name,
            "receiver_name": receiver_name,
        })

    return results


@router.get("/friends/search", response_model=List[FriendSearchResult])
def search_users(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    users = db.query(User).filter(
       ((User.email.ilike(f"%{query}%")) | (User.name.ilike(f"%{query}%"))),
        User.id != current_user.id,
    ).all()

    results = []
    for user in users:
        friend_request = db.query(FriendRequest).filter(
    ((FriendRequest.sender_id == current_user.id) & (FriendRequest.receiver_id == user.id)) |
    ((FriendRequest.sender_id == user.id) & (FriendRequest.receiver_id == current_user.id))
).order_by(FriendRequest.id.desc()).first()


        if not friend_request:
            status = "not_friends"
        elif friend_request.status == FriendRequestStatus.pending:
            status = "pending"
        elif friend_request.status == FriendRequestStatus.accepted:
            status = "friends"
        else:
            status = "not_friends"

        results.append(FriendSearchResult(id=user.id ,email=user.email,name = user.name ,status=status))

    return results
