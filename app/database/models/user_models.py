from app.database.db import Base
from typing import Optional
from sqlalchemy import Integer,String,Boolean,DateTime,Float,ForeignKey,func
from sqlalchemy.orm import Mapped,mapped_column,relationship
from datetime import datetime
from app.schemas.auth_schema import Roles

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    contact: Mapped[str] = mapped_column(String(10),unique=True,nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False,default=True)
    created_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True,server_default=func.now())
    role: Mapped[str] = mapped_column(String,index=True,nullable=False,default=Roles.customer,server_default=Roles.customer)
    # server_default required for filling default values during migration

    # users(with role=customers) and customers_profiles have one-one relationship
    customer_profile: Mapped["CustomerProfile"] = relationship(back_populates="user",cascade="all, delete-orphan",uselist=False)
    # users(with role=customers) and orders have one-many relationship
    orders: Mapped[Optional[list["Order"]]] = relationship(back_populates="user",cascade="all, delete-orphan",uselist=True)

class CustomerProfile(Base):
    __tablename__ = "customers_profiles"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    loyalty_points: Mapped[float] = mapped_column(Float,nullable=False,default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean,nullable=False,default=False)
    image_url: Mapped[str] = mapped_column(String(500),nullable=True,server_default=None)
    image_public_id: Mapped[str] = mapped_column(String(200),index=True,nullable=True,server_default=None)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),unique=True)
    user: Mapped["User"] = relationship(back_populates="customer_profile",uselist=False)