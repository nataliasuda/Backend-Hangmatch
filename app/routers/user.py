from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from jose import JWTError, jwt
from app import crud, models, schemas
from app import auth
from app.models import User
from app.auth import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, create_access_token, create_refresh_token
from app.database import get_db
from app.dependencies import get_current_user
from sqlalchemy.orm import Session
from app.schemas import Token
from pathlib import Path

router = APIRouter()

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_access_token = create_access_token(data={"sub": user_id})
    return {"access_token": new_access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.Message)
def register_user(user: schemas.UserRegister, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if crud.get_user_by_name(db, user.name):
        raise HTTPException(status_code=400, detail="Name already taken")
    created_user = crud.create_user(db, user)
    if not created_user:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    return {"message": "Account successfully registered."}

@router.post("/login", response_model=schemas.Token)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.id}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": db_user.id})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/users/me", response_model=schemas.UserRead)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: str, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users", response_model=list[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

@router.put("/users/me", response_model=schemas.UserRead)
def update_user_profile(
    updated_user: schemas.UserUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if updated_user.email != user.email:
        existing_user = crud.get_user_by_email(db, updated_user.email)
        if existing_user and existing_user.id != user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
        
    if updated_user.name != user.name:
        existing_user_by_name = crud.get_user_by_name(db, updated_user.name)
        if existing_user_by_name and existing_user_by_name.id != user.id:
            raise HTTPException(status_code=400, detail="Name already taken")
    

    user.name = updated_user.name
    user.email = updated_user.email

    if updated_user.password and updated_user.password.strip():
      
        user.password = auth.get_password_hash(updated_user.password)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
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


@router.put("/users/me/avatar", response_model=schemas.UserRead)
async def update_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    print(f" Upload avatara dla user: {current_user.id}")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        avatars_dir = Path("static/avatars")
        avatars_dir.mkdir(parents=True, exist_ok=True)
        
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        filename = f"{current_user.id}.{file_extension}"
        file_path = avatars_dir / filename
        
        print(f" Zapisuję: {file_path}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        avatar_url = f"/static/avatars/{filename}"
        
        user = db.query(models.User).filter(models.User.id == current_user.id).first()
        user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
        
        print(f" Avatar zaktualizowany: {avatar_url}")
        return user
        
    except Exception as e:
        print(f" Błąd: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/me/avatar", response_model=schemas.UserRead)
def delete_avatar(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    
    if user.avatar_url:
        file_path = Path("static/avatars") / f"{current_user.id}.jpg"
        if file_path.exists():
            file_path.unlink()
    
    user.avatar_url = None
    db.commit()
    db.refresh(user)
    
    return user