from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load .env file explicitly
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
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

# Create the users table if it doesn't exist
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI()

# Define the request schema
class UserCreate(BaseModel):
    username: str
    password: str

# Define the endpoint to add a user
@app.post("/add-user/")
def add_user(user: UserCreate):
    db = SessionLocal()
    db_user = User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return {"message": f"User {user.username} added successfully"}
