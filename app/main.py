from fastapi import FastAPI, Depends, Form
from sqlalchemy.exc import SQLAlchemyError

from app.database import *
from app.token_func import *
from app.models import UserModel

app = FastAPI()

@app.post("/users/")
async def create_user(user: UserModel,
    db: Session = Depends(get_db)
):
    if len(user.password) < 8 or user.password.isdigit():
        raise HTTPException(status_code=400,
                            detail="Password must be at least 8 characters long and contain at least one number")
    if user.salary <= 0:
        raise HTTPException(status_code=400,
                            detail="Salary must be greater than zero")
    try:
        new_password = hash_password(user.password)
        user = Users(login=user.login, password=new_password, salary=user.salary, upgrade_date=user.upgrade_date)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"login": user.login, "salary": user.salary, "upgrade_date": user.upgrade_date}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Database error: {e}"
        )

@app.get("/get_token/")
async def get_token(login: str, password: str, db: Session = Depends(get_db)):
    stmt = select(Users).where(Users.login == login)
    user = db.scalars(stmt).first()
    if not user or not check_password(password, user.password):
        raise HTTPException(status_code=404, detail="Сheck the data you entered")
    token = create_jwt_token({"id": user.id}, timedelta(minutes=15))
    return token

@app.get("/get_salary/")
async def get_salary(token: str, db: Session = Depends(get_db)):
    user = get_user_from_token(token, db)
    return {"salary": user.salary, "upgrade_date": user.upgrade_date}

@app.patch("/update_salary/")
async def update_salary(id: int = Form(...),
    salary: float = Form(...),
    upgrade_date: datetime = Form(...),
    db: Session = Depends(get_db)
):
    stmt = select(Users).where(Users.id == id)
    user = db.scalars(stmt).first()
    if not user:
        raise HTTPException(status_code=404, detail="Wrong id")
    user.salary = salary
    user.upgrade_date = upgrade_date
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return user

#Данная ручка нужна только для тестирования
@app.get("/users/")
async def get_users(db: Session = Depends(get_db)):
    users = select(Users)
    return db.scalars(users).all()

    #users = db.scalars(select(Users)).all()
    #return [{"login": user.login} for user in users]

@app.get("/user/")
async def get_user(id: int, db: Session = Depends(get_db)):
    stmt = select(Users).where(Users.id == id)
    person = db.scalars(stmt).first()
    if person is None:
        raise HTTPException(status_code=404, detail="No such user")
    return person
