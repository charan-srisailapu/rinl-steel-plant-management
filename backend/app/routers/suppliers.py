from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.master_data import User
from app.models.supply_chain import Supplier, SupplierMaterial, MaterialReceipt
from app.schemas.master_data import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    SupplierMaterialCreate, SupplierMaterialResponse,
    MaterialReceiptCreate, MaterialReceiptResponse,
    SupplierPerformanceItem,
)
from app.middleware.auth import get_current_user, require_role, WRITE_ROLES, READ_ROLES

router = APIRouter(prefix="/api/v1/suppliers", tags=["Suppliers"])


@router.get("", response_model=List[SupplierResponse])
async def list_suppliers(
    search: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = select(Supplier)
    if search:
        query = query.where(
            Supplier.supplier_name.ilike(f"%{search}%")
            | Supplier.supplier_code.ilike(f"%{search}%")
        )
    if city:
        query = query.where(Supplier.city.ilike(f"%{city}%"))
    query = query.offset(skip).limit(limit).order_by(Supplier.supplier_code)
    result = await db.execute(query)
    return [SupplierResponse.model_validate(s) for s in result.scalars().all()]


# ---- Material Receipts (must be before /{supplier_id}) ----
@router.get("/receipts", response_model=List[MaterialReceiptResponse])
async def list_receipts(
    supplier_id: Optional[int] = Query(None),
    material_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = select(MaterialReceipt).options(
        selectinload(MaterialReceipt.supplier),
        selectinload(MaterialReceipt.material),
        selectinload(MaterialReceipt.receiver),
    )
    if supplier_id:
        query = query.where(MaterialReceipt.supplier_id == supplier_id)
    if material_id:
        query = query.where(MaterialReceipt.material_id == material_id)
    query = query.order_by(MaterialReceipt.receipt_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    rows = result.scalars().unique().all()
    resp = []
    for r in rows:
        d = MaterialReceiptResponse.model_validate(r)
        d.supplier_name = r.supplier.supplier_name if r.supplier else None
        d.material_name = r.material.material_name if r.material else None
        d.receiver_name = r.receiver.full_name if r.receiver else None
        resp.append(d)
    return resp


@router.post("/receipts", response_model=MaterialReceiptResponse, status_code=status.HTTP_201_CREATED)
async def create_receipt(
    data: MaterialReceiptCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    receipt = MaterialReceipt(**data.model_dump())
    db.add(receipt)
    await db.commit()
    await db.refresh(receipt)
    result = await db.execute(
        select(MaterialReceipt)
        .options(
            selectinload(MaterialReceipt.supplier),
            selectinload(MaterialReceipt.material),
            selectinload(MaterialReceipt.receiver),
        )
        .where(MaterialReceipt.receipt_id == receipt.receipt_id)
    )
    r = result.scalar_one()
    d = MaterialReceiptResponse.model_validate(r)
    d.supplier_name = r.supplier.supplier_name if r.supplier else None
    d.material_name = r.material.material_name if r.material else None
    d.receiver_name = r.receiver.full_name if r.receiver else None
    return d


# ---- Supplier Materials (must be before /{supplier_id}) ----
@router.post("/materials", response_model=SupplierMaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier_material(
    data: SupplierMaterialCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    sm = SupplierMaterial(**data.model_dump())
    db.add(sm)
    await db.commit()
    await db.refresh(sm)
    result = await db.execute(
        select(SupplierMaterial)
        .options(selectinload(SupplierMaterial.supplier), selectinload(SupplierMaterial.material))
        .where(SupplierMaterial.supplier_material_id == sm.supplier_material_id)
    )
    sm = result.scalar_one()
    resp = SupplierMaterialResponse.model_validate(sm)
    resp.supplier_name = sm.supplier.supplier_name if sm.supplier else None
    resp.material_name = sm.material.material_name if sm.material else None
    return resp


# ---- Supplier Performance (must be before /{supplier_id}) ----
@router.get("/performance/summary", response_model=List[SupplierPerformanceItem])
async def get_supplier_performance(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = text("""
        SELECT
            s.supplier_id,
            s.supplier_code,
            s.supplier_name,
            COUNT(mr.receipt_id) AS total_receipts,
            COALESCE(SUM(mr.quantity), 0) AS total_quantity,
            AVG(mr.quality_score) AS avg_quality_score,
            AVG(mr.unit_price) AS avg_unit_price,
            s.rating
        FROM suppliers s
        LEFT JOIN material_receipts mr ON s.supplier_id = mr.supplier_id
        GROUP BY s.supplier_id, s.supplier_code, s.supplier_name, s.rating
        ORDER BY total_quantity DESC
    """)
    result = await db.execute(query)
    rows = result.fetchall()
    return [
        SupplierPerformanceItem(
            supplier_id=row[0],
            supplier_code=row[1],
            supplier_name=row[2],
            total_receipts=row[3] or 0,
            total_quantity=float(row[4]) if row[4] else 0,
            avg_quality_score=float(row[5]) if row[5] else None,
            avg_unit_price=float(row[6]) if row[6] else None,
            rating=float(row[7]) if row[7] else None,
        )
        for row in rows
    ]


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    result = await db.execute(select(Supplier).where(Supplier.supplier_id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return SupplierResponse.model_validate(supplier)


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return SupplierResponse.model_validate(supplier)


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(select(Supplier).where(Supplier.supplier_id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(supplier, key, value)
    await db.commit()
    await db.refresh(supplier)
    return SupplierResponse.model_validate(supplier)


@router.delete("/{supplier_id}")
async def delete_supplier(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(select(Supplier).where(Supplier.supplier_id == supplier_id))
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    supplier.is_active = False
    await db.commit()
    return {"message": "Supplier deactivated successfully"}


# ---- Supplier Materials ----
@router.get("/{supplier_id}/materials", response_model=List[SupplierMaterialResponse])
async def list_supplier_materials(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = (
        select(SupplierMaterial)
        .where(SupplierMaterial.supplier_id == supplier_id)
    )
    result = await db.execute(query)
    items = result.scalars().all()
    resp = []
    for sm in items:
        d = SupplierMaterialResponse.model_validate(sm)
        if sm.supplier:
            d.supplier_name = sm.supplier.supplier_name
        if sm.material:
            d.material_name = sm.material.material_name
        resp.append(d)
    return resp



