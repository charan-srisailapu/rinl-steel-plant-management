from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.master_data import MaterialMaster
from app.schemas.master_data import MaterialMasterCreate, MaterialMasterUpdate, MaterialMasterResponse
from app.middleware.auth import get_current_user, require_role, WRITE_ROLES
from app.models.master_data import User

router = APIRouter(prefix="/api/v1/materials", tags=["Materials"])


@router.get("", response_model=List[MaterialMasterResponse])
async def list_materials(
    search: Optional[str] = Query(None),
    material_type: Optional[str] = Query(None),
    material_group: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(MaterialMaster).options(selectinload(MaterialMaster.uom))

    if search:
        query = query.where(
            MaterialMaster.material_name.ilike(f"%{search}%")
            | MaterialMaster.material_code.ilike(f"%{search}%")
        )
    if material_type:
        query = query.where(MaterialMaster.material_type == material_type)
    if material_group:
        query = query.where(MaterialMaster.material_group == material_group)

    query = query.offset(skip).limit(limit).order_by(MaterialMaster.material_code)
    result = await db.execute(query)
    return [MaterialMasterResponse.model_validate(m) for m in result.scalars().unique().all()]


@router.get("/{material_id}", response_model=MaterialMasterResponse)
async def get_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MaterialMaster)
        .options(selectinload(MaterialMaster.uom))
        .where(MaterialMaster.material_id == material_id)
    )
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return MaterialMasterResponse.model_validate(material)


@router.post("", response_model=MaterialMasterResponse, status_code=status.HTTP_201_CREATED)
async def create_material(
    data: MaterialMasterCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    material = MaterialMaster(**data.model_dump())
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return MaterialMasterResponse.model_validate(material)


@router.put("/{material_id}", response_model=MaterialMasterResponse)
async def update_material(
    material_id: int,
    data: MaterialMasterUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(
        select(MaterialMaster).where(MaterialMaster.material_id == material_id)
    )
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(material, key, value)

    await db.commit()
    await db.refresh(material)
    return MaterialMasterResponse.model_validate(material)


@router.delete("/{material_id}")
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(
        select(MaterialMaster).where(MaterialMaster.material_id == material_id)
    )
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    material.is_active = False
    await db.commit()
    return {"message": "Material deactivated successfully"}
