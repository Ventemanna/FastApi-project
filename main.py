import psycopg2
from fastapi import FastAPI, Depends, Form, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import select

from models import Users
from database import get_db, SessionLocal

app = FastAPI()

@app.post("/users/")
async def create_user(
    login: str = Form(...),
    password: str = Form(...),
    salary: float = Form(...),
    db: Session = Depends(get_db)
):

    if len(password) < 8 or password.isdigit() or '0123456789' not in password:
        raise HTTPException(status_code=400,
                            detail="Password must be at least 8 characters long and contain at least one number")
    try:
        user = Users(login=login, password=password, salary=salary)
        db.add(user)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Database error: {e}"
        )

@app.get("/get_token/")
async def get_token(login: str, password: str, db: Session = Depends(get_db)):
    person = select(Users.login).where(Users.login == login, Users.password == password)
    if db.scalar(person) is None:
        raise HTTPException(status_code=400,detail="Login or password incorrect")
    return db.scalars(person).all()

@app.get("/users/")
async def get_users(db: Session = Depends(get_db)):
    users = select(Users)
    return db.scalars(users).all()

    #users = db.scalars(select(Users)).all()
    #return [{"login": user.login} for user in users]

@app.get("/user/")
async def get_user(id: int, db: Session = Depends(get_db)):
    person = select(Users).where(Users.id == id)
    return {"message": "Person found", "person": db.scalars(person).one()}
