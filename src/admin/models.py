from datetime import datetime
from typing import TYPE_CHECKING, List
from enum import Enum as PyEnum
from sqlalchemy import String, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from cuid2 import cuid_wrapper
from ..database import Base

cuid_generate = cuid_wrapper()

if TYPE_CHECKING:
    from ..purchases.models import Order


class UserType(str, PyEnum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=cuid_generate)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    user_type: Mapped[UserType] = mapped_column(
        "type",
        Enum(UserType, length=30, native_enum=False),
        nullable=False,
        default=UserType.user,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    orders: Mapped[List["Order"]] = relationship(
        "Order", back_populates="user", lazy="selectin"
    )
