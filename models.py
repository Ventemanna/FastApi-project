from sqlalchemy import String, Numeric, DateTime
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column
from database import engine
from datetime import datetime
from pydantic import BaseModel

#TODO Как-то сделать так чтобы salary был только позитивным числом
#TODO Поменять коды ошибок на имеющие смысл

class UserModel(BaseModel):
    login: str
    password: str
    salary: float
    upgrade_date: datetime

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    salary: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    upgrade_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
       pass

Base.metadata.create_all(bind=engine)