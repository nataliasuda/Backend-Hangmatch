from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import Base, engine, SessionLocal


app = FastAPI(
    title="HangMatch API",
    description="RESTful API for managing sessions, users, and shared activity voting in the HangMatch app — designed for social interaction and decision-making.",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemas.Message)
def register_user(user: schemas.UserRegister, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    created_user = crud.create_user(db, user)
    if not created_user:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    return {"message": "Account successfully registered."}


@app.post("/login", response_model=schemas.Message)
def login_user(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful."}



@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users", response_model=list[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)
