from sqlalchemy import String, Numeric
from sqlalchemy.orm import DeclarativeBase,Mapped, mapped_column
from database import engine

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(50))
    salary: Mapped[float] = mapped_column(Numeric(10, 2))

    def __repr__(self):
       pass

Base.metadata.create_all(bind=engine)