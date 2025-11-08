from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import jwt
import requests
import time
import threading
import bcrypt
import os

# redeploy
# redeploy

# Load .env file
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(username: str):
    payload = {"sub": username, "iat": datetime.utcnow()}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token_and_get_username(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

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

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key= True, index= True)
    username = Column(String, index= True)
    content = Column(String)
    timestamp = Column(String)

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

class MessageCreate(BaseModel):
    token: str
    content: str

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
        
        token = create_access_token(db_user.username)
        return {"message": f"User {user.username} added successfully", "access_token" : token}

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
        
        token = create_access_token(db_user.username)
        return {"message": f"Welcome back, {user.username}!", "access_token" : token}

@app.get("/ping/")
def ping():
    return {"status" : "alive"}

@app.post("/chat/")
def send_message(msg: MessageCreate):
    username = verify_token_and_get_username(msg.token)

    with SessionLocal() as db:
        db_msg = Message(
            username = username,
            content = msg.content,
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        )
        db.add(db_msg)
        db.commit()
        db.refresh(db_msg)

        total = db.query(Message).count()
        if total > 50:
            old_ids = (
                db.query(Message.id)
                .order_by(Message.id.desc())
                .offset(50)
                .all()
            )

            old_ids = [row.id for row in old_ids]
            if old_ids:
                db.query(Message).filter(Message.id.in_(old_ids)).delete(synchronize_session=False)
                db.commit()

        return {"message": "Message sent!", "id": db_msg.id}

@app.get("/chat/")
def get_messages():
    with SessionLocal() as db:
        # Fetch the latest 50 messages
        messages = db.query(Message).order_by(Message.id.desc()).limit(50).all()
        # Reverse to show oldest first
        messages.reverse()

        # Return them to API callers too
        return [
            {"username": m.username, "content": m.content, "timestamp": m.timestamp}
            for m in messages
        ]

def keep_alive():
    while True:
        try:
            requests.get("https://fastapi-app-cr0h.onrender.com/ping/")
        except Exception:
            pass
        time.sleep(300)  # every 5 minutes

threading.Thread(target=keep_alive, daemon=True).start()
