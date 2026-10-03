from sqlalchemy import Integer, ForeignKey, Text, DateTime, Boolean, CheckConstraint, text
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.database import Base
from datetime import datetime


class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    grade: Mapped[int] = mapped_column(CheckConstraint("grade >= 1 AND grade <= 5"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped['User'] = relationship('User', back_populates='reviews')
    products: Mapped['Product'] = relationship('Product', back_populates='reviews')