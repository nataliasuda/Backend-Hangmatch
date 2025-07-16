from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app import crud, models, schemas
from app.crud import create_session
from app.database import get_db
from app.dependencies import get_current_user
from sqlalchemy.orm import Session
from app.models import User


router = APIRouter()

@router.post("/sessions", response_model=schemas.SessionOut)
def create_new_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
     new_session = create_session(db=db, session_data=session_data, owner_id=current_user.id)
     return schemas.SessionOut(
        id=new_session.id,
        name=new_session.name,
        location_radius=new_session.location_radius,
        owner_id=new_session.owner_id,
        invited_users_ids=[user.id for user in new_session.invited_users],
        created_at=new_session.created_at
    )

@router.get("/sessions/me", response_model=List[schemas.SessionOut])
def get_my_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = crud.get_sessions_for_user(db, current_user.id)
    return [
        schemas.SessionOut(
            id=s.id,
            name=s.name,
            location_radius=s.location_radius,
            owner_id=s.owner_id,
            invited_users_ids=[u.id for u in s.invited_users],
            created_at=s.created_at
        )
        for s in sessions
    ]


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = db.query(models.Session).filter(models.Session.id == session_id.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only owner can delete the session")

    db.delete(session)
    db.commit()
    return 


@router.delete("/leave/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def leave_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    session = db.query(models.Session).filter(models.Session.id == session_id.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if current_user in session.invited_users:
        session.invited_users.remove(current_user)
        db.commit()

    
    return
