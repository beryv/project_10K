from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# SQLite database file path inside the container
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# Setup SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Define the User Database Model
class UserDB(Base):
  __tablename__ = "users"
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, index=True)


# Create tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Pydantic model for request validation
class UserCreate(BaseModel):
  name: str


# Dependency to get the database session
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


@app.get("/")
def read_root():
  return {"message": "Python API with SQLite is running!"}


# Endpoint to add a user to the database
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
  db_user = UserDB(name=user.name)
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return {"id": db_user.id, "name": db_user.name}


# Endpoint to fetch all users from the database
@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
  users = db.query(UserDB).all()
  return users