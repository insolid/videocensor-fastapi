import enum

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Role(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(SQLAlchemyBaseUserTable[int], Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER)

    videojobs: Mapped[list["VideoJob"]] = relationship(back_populates="user")
    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
