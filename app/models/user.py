from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.session import session_user_association
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    
    invited_sessions = relationship("Session", secondary=session_user_association, back_populates="invited_users")
    owned_sessions = relationship("Session", back_populates="owner")

