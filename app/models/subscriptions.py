from datetime import date
from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Plan(Base):
    __tablename__ = "plan"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    duration_months: Mapped[int] = mapped_column()
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    currency: Mapped[str] = mapped_column()


class Subscription(Base):
    __tablename__ = "subscription"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    start_date: Mapped[date | None] = mapped_column()
    end_date: Mapped[date | None] = mapped_column()

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="subscriptions")
    plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("plan.id", ondelete="CASCADE")
    )
    plan: Mapped["Plan"] = relationship()
