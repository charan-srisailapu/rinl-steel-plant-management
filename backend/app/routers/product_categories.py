from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.master_data import User
from app.models.supply_chain import ProductCategory
from app.schemas.master_data import ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryResponse
from app.middleware.auth import get_current_user, require_role, WRITE_ROLES, READ_ROLES

router = APIRouter(prefix="/api/v1/product-categories", tags=["Product Categories"])


@router.get("", response_model=List[ProductCategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    result = await db.execute(select(ProductCategory).order_by(ProductCategory.category_name))
    return [ProductCategoryResponse.model_validate(c) for c in result.scalars().all()]


@router.post("", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: ProductCategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    cat = ProductCategory(**data.model_dump())
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return ProductCategoryResponse.model_validate(cat)
