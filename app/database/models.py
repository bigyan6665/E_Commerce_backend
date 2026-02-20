from app.database.db import Base
from typing import Optional,List
from sqlalchemy import Integer,String,Boolean,DateTime,Float,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from datetime import datetime, timezone
from app.schemas.auth import Roles

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    contact: Mapped[str] = mapped_column(String(10),unique=True,index=True,nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True,default=True)
    created_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False, index=True,default=datetime.now(timezone.utc))
    role: Mapped[str] = mapped_column(String,index=True,nullable=False,default=Roles.customer,server_default=Roles.customer)
    # server_default required for filling default values during migration

    # users(with role=customers) and customers_profiles have one-one relationship
    customer_profile: Mapped[Optional["CustomerProfile"]] = relationship(back_populates="user",cascade="all, delete-orphan",uselist=False)
    # users(with role=customers) and orders have one-many relationship
    orders: Mapped[Optional[list["Order"]]] = relationship(back_populates="user",cascade="all, delete-orphan")

class CustomerProfile(Base):
    __tablename__ = "customers_profiles"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    loyalty_points: Mapped[float] = mapped_column(Float,index=True,nullable=False,default=0)
    is_verified: Mapped[bool] = mapped_column(Boolean,nullable=False,default=False)
    image_url: Mapped[str] = mapped_column(String(500),index=True,nullable=True,default=None,server_default=None)
    image_public_id: Mapped[str] = mapped_column(String(200),index=True,nullable=True,default=None,server_default=None)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),unique=True)
    user: Mapped["User"] = relationship(back_populates="customer_profile")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    order_date: Mapped[DateTime] = mapped_column(DateTime,nullable=False,index=True,default=datetime.now(timezone.utc))
    total_amount: Mapped[Float] = mapped_column(Float,nullable=False,index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="orders")

    # orders and products have many-many relationship via order_items
    # 1-many(orders,order_items) and many-1(order_items,products)
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order",cascade="all, delete-orphan")

class OrderItem(Base):
    # association table with PK = (order_id,product_id) i.e, composite PK
    __tablename__ = "order_items"
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"),primary_key=True)
    order: Mapped["Order"] = relationship(back_populates="items")

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"),primary_key=True)
    product: Mapped["Product"] = relationship(back_populates="items") 

    quantity: Mapped[int] = mapped_column(Integer,index=True,nullable=False,default=1) 

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    name: Mapped[str] = mapped_column(String(200),nullable=False,index=True)
    price: Mapped[Float] = mapped_column(Float,nullable=False,index=True)

    items: Mapped[List["OrderItem"]] = relationship(back_populates="product",cascade="all, delete-orphan") 

