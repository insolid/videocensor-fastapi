import enum
from decimal import Decimal

from sqlalchemy import DECIMAL, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .subscriptions import Currency


class Status(str, enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Payment(Base):
    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2))
    currency: Mapped[Currency] = mapped_column(Enum(Currency))
    method: Mapped[str] = mapped_column()
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PROCESSING)

    subscription_id: Mapped[int | None] = mapped_column(
        ForeignKey("subscription.id", ondelete="SET NULL")
    )
    subscription: Mapped["Subscription"] = relationship()
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship()
