from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta

from app import models, schemas, crud
from app.database import SessionLocal, engine, Base
from app.auth import create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import User
from app.crud import create_session

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="HangMatch API",
    description="RESTful API for managing sessions, users, and shared activity voting in the HangMatch app — designed for social interaction and decision-making.",
    version="1.0.0",
    
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
user_router = APIRouter(tags=["users"])
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user(db, user_id)
    if user is None:
        raise credentials_exception
    return user

@user_router.post("/register", response_model=schemas.Message)
def register_user(user: schemas.UserRegister, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = crud.create_user(db, user)
    if not created_user:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    return {"message": "Account successfully registered."}

@user_router.post("/login", response_model=schemas.Token)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"user_id": db_user.id}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("/users/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@user_router.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@user_router.get("/users", response_model=list[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

@user_router.put("/users/me", response_model=schemas.UserRead)
def update_user_profile(
    updated_user: schemas.UserRegister, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    

    user.name = updated_user.name
    user.email = updated_user.email

    db.commit()
    db.refresh(user)
    return user

@user_router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_account(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return 
app.include_router(user_router)


session_router = APIRouter(prefix="/sessions", tags=["sessions"])

@session_router.post("/", response_model=schemas.SessionOut)
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

@session_router.get("/me", response_model=List[schemas.SessionOut])
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

app.include_router(session_router)