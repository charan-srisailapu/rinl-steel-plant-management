from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.master_data import ProductCatalog
from app.schemas.master_data import ProductCatalogCreate, ProductCatalogUpdate, ProductCatalogResponse
from app.middleware.auth import get_current_user, require_role, WRITE_ROLES
from app.models.master_data import User

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.get("", response_model=List[ProductCatalogResponse])
async def list_products(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    product_group: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(ProductCatalog).options(selectinload(ProductCatalog.uom))

    if search:
        query = query.where(
            ProductCatalog.product_name.ilike(f"%{search}%")
            | ProductCatalog.product_code.ilike(f"%{search}%")
        )
    if category:
        query = query.where(ProductCatalog.product_category == category)
    if product_group:
        query = query.where(ProductCatalog.product_group == product_group)

    query = query.offset(skip).limit(limit).order_by(ProductCatalog.product_code)
    result = await db.execute(query)
    return [ProductCatalogResponse.model_validate(p) for p in result.scalars().unique().all()]


@router.get("/{product_id}", response_model=ProductCatalogResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ProductCatalog)
        .options(selectinload(ProductCatalog.uom))
        .where(ProductCatalog.product_id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductCatalogResponse.model_validate(product)


@router.post("", response_model=ProductCatalogResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCatalogCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    product = ProductCatalog(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return ProductCatalogResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductCatalogResponse)
async def update_product(
    product_id: int,
    data: ProductCatalogUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(
        select(ProductCatalog).where(ProductCatalog.product_id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    return ProductCatalogResponse.model_validate(product)


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(
        select(ProductCatalog).where(ProductCatalog.product_id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = False
    await db.commit()
    return {"message": "Product deactivated successfully"}
