from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.master_data import UomMaster
from app.schemas.master_data import UomMasterCreate, UomMasterUpdate, UomMasterResponse
from app.middleware.auth import get_current_user, require_role, WRITE_ROLES
from app.models.master_data import User

router = APIRouter(prefix="/api/v1/uom", tags=["UOM"])


@router.get("", response_model=List[UomMasterResponse])
async def list_uom(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(UomMaster).offset(skip).limit(limit).order_by(UomMaster.uom_code)
    )
    return [UomMasterResponse.model_validate(u) for u in result.scalars().all()]


@router.post("", response_model=UomMasterResponse, status_code=status.HTTP_201_CREATED)
async def create_uom(
    data: UomMasterCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    uom = UomMaster(**data.model_dump())
    db.add(uom)
    await db.commit()
    await db.refresh(uom)
    return UomMasterResponse.model_validate(uom)
