from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, update

from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.schemas import Review as ReviewSchema, ReviewCreate

from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db

from app.models.users import User as UserModel
from app.auth import get_current_buyer, get_current_user

from sqlalchemy.sql import func


router = APIRouter(
    prefix='/reviews',
    tags=['reviews']
)


async def update_product_rating(db: AsyncSession, product_id: int):
    '''Функция для расчёта среднего grade'''
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()


@router.get('/', response_model=list[ReviewSchema], status_code=status.HTTP_200_OK)
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    '''Возвращает список всех отзывов'''
    result = await db.scalars(select(ReviewModel).where(ReviewModel.is_active == True))
    return result.all()


@router.get('/products/{prod_id}/reviews',
             response_model=list[ReviewSchema],
            status_code=status.HTTP_200_OK)
async def get_review_by_product(
    prod_id: int,
    db: AsyncSession = Depends(get_async_db)
    ):
    '''Получение отзывов о конкретном товаре'''
    result = await db.scalars(select(ProductModel).where(ProductModel.id == prod_id,
                                                         ProductModel.is_active == True))
    product = result.first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    reviews = await db.scalars(select(ReviewModel).where(ReviewModel.product_id == product.id,
                                                                ReviewModel.is_active == True))
    return reviews.all()


@router.post('/', response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate, 
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_buyer)
    ):
    '''Добавление отзыва.'''
    result_product = await db.scalars(select(ProductModel).where(ProductModel.id == review.product_id,
                                                                 ProductModel.is_active == True))
    product = result_product.first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await update_product_rating(db, product.id)
    await db.commit()
    await db.refresh(db_review)
    return db_review


@router.delete('/{review_id}', response_model=dict, status_code=status.HTTP_200_OK)
async def delete_review(
    review_id: int, 
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user)
    ):
    '''Мягкое удаление отзыва'''
    result = await db.scalars(select(ReviewModel).where(ReviewModel.id == review_id,
                                                        ReviewModel.is_active == True))
    review = result.first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if review.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    review.is_active = False
    await update_product_rating(db, review.product_id)
    await db.commit()
    await db.refresh(review)
    return {"message": "Review deleted"}