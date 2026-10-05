from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(String, default='buyer')

    products: Mapped[list['Product']] = relationship('Product', back_populates='seller')
    category: Mapped[list['Category']] = relationship('Category', back_populates='admin')
    reviews: Mapped[list['Review']] = relationship('Review', back_populates='user')
    cart_items: Mapped[list['CartItems']] = relationship('CartItems', 
                                                             back_populates='product',
                                                             cascade='all, delete-orphan')