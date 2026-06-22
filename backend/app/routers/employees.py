from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.organization import Employee
from app.schemas.organization import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.middleware.auth import get_current_user, require_role, WRITE_ROLES
from app.models.master_data import User

router = APIRouter(prefix="/api/v1/employees", tags=["Employees"])


@router.get("", response_model=List[EmployeeResponse])
async def list_employees(
    search: Optional[str] = Query(None),
    dept_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = select(Employee).options(
        selectinload(Employee.department),
        selectinload(Employee.designation),
        selectinload(Employee.unit),
        selectinload(Employee.shift),
    )

    if search:
        query = query.where(
            Employee.full_name.ilike(f"%{search}%")
            | Employee.emp_number.ilike(f"%{search}%")
            | Employee.email.ilike(f"%{search}%")
        )
    if dept_id:
        query = query.where(Employee.dept_id == dept_id)

    query = query.offset(skip).limit(limit).order_by(Employee.emp_number)
    result = await db.execute(query)
    return [EmployeeResponse.model_validate(e) for e in result.scalars().unique().all()]


@router.get("/{emp_id}", response_model=EmployeeResponse)
async def get_employee(
    emp_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Employee)
        .options(
            selectinload(Employee.department),
            selectinload(Employee.designation),
            selectinload(Employee.unit),
            selectinload(Employee.shift),
        )
        .where(Employee.emp_id == emp_id)
    )
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeResponse.model_validate(emp)


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    emp = Employee(**data.model_dump())
    db.add(emp)
    await db.commit()
    await db.refresh(emp)
    return EmployeeResponse.model_validate(emp)


@router.put("/{emp_id}", response_model=EmployeeResponse)
async def update_employee(
    emp_id: int,
    data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(select(Employee).where(Employee.emp_id == emp_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(emp, key, value)

    await db.commit()
    await db.refresh(emp)
    return EmployeeResponse.model_validate(emp)


@router.delete("/{emp_id}")
async def delete_employee(
    emp_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(select(Employee).where(Employee.emp_id == emp_id))
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    emp.is_active = False
    await db.commit()
    return {"message": "Employee deactivated successfully"}
