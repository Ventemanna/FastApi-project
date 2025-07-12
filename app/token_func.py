import hashlib
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from jwt import ExpiredSignatureError
from passlib.exc import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import algorith, secret_key
from app.models import Users

def create_jwt_token(data: dict, time: timedelta):
    information = data.copy()
    expire = datetime.now(timezone.utc) + time
    information["exp"] = expire
    return jwt.encode(information, secret_key, algorithm=algorith)

def get_user_from_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorith)
        id = payload.get("id")
        if id is None:
            raise HTTPException(status_code=400,
                            detail="No user found")
        user = select(Users).where(Users.id == id)
        return db.scalars(user).first()
    except ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token is expired")
    except (InvalidTokenError, jwt.exceptions.DecodeError):
        raise HTTPException(status_code=400, detail="Invalid token")

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password: str, hashed_password: str):
    return hashlib.sha256(password.encode()).hexdigest() == hashed_password