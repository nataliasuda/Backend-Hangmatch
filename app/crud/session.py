from datetime import datetime
from app import schemas, models
from app.models import Session

def create_session(db: Session, session_data: schemas.SessionCreate, owner_id: str):
    invited_users = db.query(models.User).filter(models.User.id.in_(session_data.invited_users_ids)).all()
    new_session = models.Session(
        name=session_data.name,
        location_radius=session_data.location_radius,
        owner_id=owner_id,
        invited_users=invited_users,
        created_at=datetime.utcnow()

    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def get_sessions_for_user(db: Session, user_id: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return []

    sessions = user.owned_sessions + user.invited_sessions
    return sorted(sessions, key=lambda s: s.created_at or datetime.min,  reverse=True)