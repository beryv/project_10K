from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./bank.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


def initialize_database():
  Base.metadata.create_all(bind=engine)
  transaction_columns = {
      column["name"] for column in inspect(engine).get_columns("transactions")
  }
  if "description" not in transaction_columns:
    with engine.begin() as connection:
      connection.execute(
          text("ALTER TABLE transactions ADD COLUMN description VARCHAR DEFAULT ''")
      )