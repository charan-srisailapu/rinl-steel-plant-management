from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.organization import ProductionUnit
from app.schemas.organization import ProductionUnitCreate, ProductionUnitUpdate, ProductionUnitResponse
from app.middleware.auth import get_current_user, require_role, WRITE_ROLES
from app.models.master_data import User

router = APIRouter(prefix="/api/v1/units", tags=["Production Units"])


@router.get("", response_model=List[ProductionUnitResponse])
async def list_units(
    dept_id: Optional[int] = Query(None),
    unit_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(ProductionUnit).options(selectinload(ProductionUnit.department))

    if dept_id:
        query = query.where(ProductionUnit.dept_id == dept_id)
    if unit_type:
        query = query.where(ProductionUnit.unit_type == unit_type)

    query = query.offset(skip).limit(limit).order_by(ProductionUnit.unit_code)
    result = await db.execute(query)
    return [ProductionUnitResponse.model_validate(u) for u in result.scalars().unique().all()]


@router.get("/{unit_id}", response_model=ProductionUnitResponse)
async def get_unit(
    unit_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ProductionUnit)
        .options(selectinload(ProductionUnit.department))
        .where(ProductionUnit.unit_id == unit_id)
    )
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException(status_code=404, detail="Production unit not found")
    return ProductionUnitResponse.model_validate(unit)


@router.post("", response_model=ProductionUnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(
    data: ProductionUnitCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    unit = ProductionUnit(**data.model_dump())
    db.add(unit)
    await db.commit()
    await db.refresh(unit)
    return ProductionUnitResponse.model_validate(unit)


@router.put("/{unit_id}", response_model=ProductionUnitResponse)
async def update_unit(
    unit_id: int,
    data: ProductionUnitUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(
        select(ProductionUnit).where(ProductionUnit.unit_id == unit_id)
    )
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException(status_code=404, detail="Production unit not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(unit, key, value)

    await db.commit()
    await db.refresh(unit)
    return ProductionUnitResponse.model_validate(unit)


@router.delete("/{unit_id}")
async def delete_unit(
    unit_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(
        select(ProductionUnit).where(ProductionUnit.unit_id == unit_id)
    )
    unit = result.scalar_one_or_none()
    if not unit:
        raise HTTPException(status_code=404, detail="Production unit not found")

    unit.is_active = False
    await db.commit()
    return {"message": "Production unit deactivated successfully"}
