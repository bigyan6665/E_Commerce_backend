
from app.database.db import Base
from sqlalchemy import Integer,DateTime,Float,ForeignKey,func
from sqlalchemy.orm import Mapped,mapped_column,relationship
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    order_date: Mapped[datetime] = mapped_column(DateTime,nullable=False,index=True,server_default=func.now())
    total_amount: Mapped[float] = mapped_column(Float,nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="orders",uselist=False)

    # orders and products have many-many relationship via order_items
    # 1-many(orders,order_items) and many-1(order_items,products)
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order",cascade="all, delete-orphan",uselist=True)

class OrderItem(Base):
    # association table with PK = (order_id,product_id) i.e, composite PK
    __tablename__ = "order_items"
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"),primary_key=True)
    order: Mapped["Order"] = relationship(back_populates="items",uselist=False)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"),primary_key=True)
    product: Mapped["Product"] = relationship(back_populates="items",uselist=False) 

    quantity: Mapped[int] = mapped_column(Integer,nullable=False,default=1) 


