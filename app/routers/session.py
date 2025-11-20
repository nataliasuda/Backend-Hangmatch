from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app import crud, models, schemas
from app.database import get_db
from app.dependencies import get_current_user
from sqlalchemy.orm import Session as DBSession
from app.models import User


router = APIRouter()

@router.post("/sessions", response_model=schemas.SessionOut)
def create_draft_session(session_data: schemas.SessionCreate, db: DBSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = models.Session(
        name=session_data.name,
        location_radius=session_data.location_radius,
        owner_id=current_user.id,
        status='draft',
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return schemas.SessionOut(
        id=session.id,
        name=session.name,
        location_radius=session.location_radius,
        owner_id=session.owner_id,
        invited_users_ids=[],       
        created_at=session.created_at,
        status=session.status,      
    )



@router.get("/sessions/me", response_model=List[schemas.SessionOut])
def get_my_sessions(db: DBSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = crud.get_sessions_for_user(db, current_user.id)
    return [
        schemas.SessionOut(
            id=s.id,
            name=s.name,
            location_radius=s.location_radius,
            owner_id=s.owner_id,
            invited_users_ids=[str(u.id) for u in s.invited_users], 
            created_at=s.created_at,
            status=s.status,  
        )
        for s in sessions
    ]


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    db: DBSession = Depends(get_db), 
    current_user: models.User = Depends(get_current_user),
):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
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
    db: DBSession = Depends(get_db), 
    current_user: models.User = Depends(get_current_user),
):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session_user = (
        db.query(models.SessionUser)
        .filter_by(user_id=current_user.id, session_id=session_id)
        .first()
    )

    if not session_user:
        raise HTTPException(status_code=404, detail="User is not part of this session")

    session_user.status = 'left'
    db.commit()

    return



@router.get("/invitations/me")
def get_my_invitations(
    db: DBSession = Depends(get_db), 
    current_user: models.User = Depends(get_current_user),
):
    invitations = db.query(models.SessionUser).filter_by(user_id = current_user.id, status= 'invited').join(models.Session).all()  # DODAJ models.

    return [
        {
            'session_id': assoc.session.id,
            'session_name': assoc.session.name,
            'invited_by': assoc.session.owner.name
        }
        for assoc in invitations
    ]

@router.post("/sessions/join/{session_id}")
def join_session(session_id: str, db: DBSession = Depends(get_db), current_user: User = Depends(get_current_user)):  # ZMIEŃ TUTAJ
    invitation = db.query(models.SessionUser).filter_by(user_id=current_user.id, session_id=session_id, status='invited').first()
    if not invitation:
        raise HTTPException(status_code=403, detail="No invitation found")

    invitation.status = 'joined'
    db.commit()
    return {"detail": "You have joined the session"}


@router.post("/sessions/reject/{session_id}")
def reject_session(
    session_id: str,
    db: DBSession = Depends(get_db),  # ZMIEŃ TUTAJ
    current_user: models.User = Depends(get_current_user),
):
    association = db.query(models.SessionUser).filter_by(
        session_id=session_id,
        user_id=current_user.id
    ).first()

    if not association:
        raise HTTPException(status_code=404, detail="Invitation not found")

    association.status = "rejected"
    db.commit()

    return {"message": "You have rejected the session invitation"}

@router.post("/sessions/invite/{session_id}")
def invite_users_to_session(
    session_id: str,
    request: schemas.SessionInvitationRequest, 
    db: DBSession = Depends(get_db),  # ZMIEŃ TUTAJ
    current_user: User = Depends(get_current_user),
):
    session = db.query(models.Session).filter_by(id=session_id, owner_id=current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not yours")

    for email in request.emails:
        user = db.query(models.User).filter_by(email=email).first()
        if user:
            existing = db.query(models.SessionUser).filter_by(user_id=user.id, session_id=session_id).first()
            if not existing:
                invitation = models.SessionUser(user_id=user.id, session_id=session_id, status='invited')
                db.add(invitation)

    db.commit()
    return {"detail": "Invitations sent"}


@router.post("/sessions/activate/{session_id}")
def activate_session(session_id: str, db: DBSession = Depends(get_db), current_user: User = Depends(get_current_user)):  # ZMIEŃ TUTAJ
    session = db.query(models.Session).filter_by(id=session_id, owner_id=current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or not yours")
    
    joined_count = db.query(models.SessionUser).filter_by(session_id=session_id, status='joined').count()
    if joined_count == 0:
        raise HTTPException(status_code=400, detail="At least one friend must join to activate")

    session.status = 'active'
    db.commit()
    return {"detail": "Session activated"}