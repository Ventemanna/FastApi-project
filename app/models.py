from sqlalchemy import String, Numeric, DateTime
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column
from app.database import engine
from datetime import datetime
from pydantic import BaseModel

class UserModel(BaseModel):
    login: str
    password: str
    salary: float
    upgrade_date: datetime

class UpdateSalaryModel(BaseModel):
    id: int
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

Base.metadata.create_all(bind=engine)