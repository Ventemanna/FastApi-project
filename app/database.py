from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

env_path = '../.env'
load_dotenv(dotenv_path=env_path)

print(os.getenv("DATABASE_URL"))

base_url = os.getenv("DATABASE_URL")
algorith = os.getenv("ALGORITH")
secret_key = os.getenv("SECRET_KEY")

engine = create_engine(base_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
