from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.organization import Department
from app.schemas.organization import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse, DepartmentTreeResponse,
)
from app.middleware.auth import get_current_user, require_role, WRITE_ROLES
from app.models.master_data import User

router = APIRouter(prefix="/api/v1/departments", tags=["Departments"])


@router.get("", response_model=List[DepartmentResponse])
async def list_departments(
    search: Optional[str] = Query(None),
    dept_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Department)

    if search:
        query = query.where(
            Department.dept_name.ilike(f"%{search}%")
            | Department.dept_code.ilike(f"%{search}%")
        )
    if dept_type:
        query = query.where(Department.dept_type == dept_type)

    query = query.offset(skip).limit(limit).order_by(Department.dept_code)
    result = await db.execute(query)
    return [DepartmentResponse.model_validate(d) for d in result.scalars().all()]


@router.get("/tree", response_model=List[DepartmentTreeResponse])
async def get_department_tree(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Department).options(selectinload(Department.children)).where(
        Department.parent_dept_id.is_(None)
    )
    result = await db.execute(query)
    return [DepartmentTreeResponse.model_validate(d) for d in result.scalars().unique().all()]


@router.get("/{dept_id}", response_model=DepartmentResponse)
async def get_department(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Department).where(Department.dept_id == dept_id)
    )
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return DepartmentResponse.model_validate(dept)


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    dept = Department(**data.model_dump())
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return DepartmentResponse.model_validate(dept)


@router.put("/{dept_id}", response_model=DepartmentResponse)
async def update_department(
    dept_id: int,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(select(Department).where(Department.dept_id == dept_id))
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(dept, key, value)

    await db.commit()
    await db.refresh(dept)
    return DepartmentResponse.model_validate(dept)


@router.delete("/{dept_id}")
async def delete_department(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(select(Department).where(Department.dept_id == dept_id))
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    dept.is_active = False
    await db.commit()
    return {"message": "Department deactivated successfully"}
