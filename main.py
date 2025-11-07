from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt
import os

# redeploy
# redeploy

# Load .env file
DATABASE_URL = os.getenv("DATABASE_URL")

# Set up SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

# Create the users table
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI()

# Request schemas
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Sign-up endpoint
@app.post("/add-user/")
def add_user(user: UserCreate):
    with SessionLocal() as db:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Hash the password before storing
        hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        
        # Create new user
        db_user = User(username=user.username, password=hashed_pw.decode('utf-8'))
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {"message": f"User {user.username} added successfully"}

# Login endpoint
@app.post("/login/")
def login(user: UserLogin):
    with SessionLocal() as db:
        # Find the user in the database
        db_user = db.query(User).filter(User.username == user.username).first()
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Assign stored hashed password to a variable for readability
        hashed_pw = db_user.password
        
        # Verify password using bcrypt
        if not bcrypt.checkpw(user.password.encode('utf-8'), hashed_pw.encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        return {"message": f"Welcome back, {user.username}!"}

@app.get("/ping/")
def ping():
    return {"status" : "alive"}