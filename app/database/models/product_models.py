from app.database.db import Base
from sqlalchemy import Integer,String,Float
from sqlalchemy.orm import Mapped,mapped_column,relationship

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(200),nullable=False,index=True,unique=True) # combination of name,category,variant, is recommended
    price: Mapped[float] = mapped_column(Float,nullable=False,index=True)
    description: Mapped[str] = mapped_column(String(500),nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer,nullable=False,default=0)

    items: Mapped[list["OrderItem"]] = relationship(back_populates="product",cascade="all, delete-orphan",uselist=True) 