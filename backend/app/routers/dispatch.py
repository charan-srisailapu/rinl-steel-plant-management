from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.master_data import User
from app.models.supply_chain import Dispatch, DispatchItem, Customer, FinishedProduct
from app.schemas.master_data import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    FinishedProductCreate, FinishedProductUpdate, FinishedProductResponse,
    DispatchCreate, DispatchUpdate, DispatchResponse,
    DispatchItemCreate, DispatchItemResponse,
    DispatchSummaryItem,
)
from app.middleware.auth import get_current_user, require_role, WRITE_ROLES, READ_ROLES

router = APIRouter(prefix="/api/v1/dispatch", tags=["Dispatch"])


# ---- Customers ----
@router.get("/customers", response_model=List[CustomerResponse])
async def list_customers(
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = select(Customer)
    if search:
        query = query.where(
            Customer.customer_name.ilike(f"%{search}%")
            | Customer.customer_code.ilike(f"%{search}%")
        )
    query = query.offset(skip).limit(limit).order_by(Customer.customer_code)
    result = await db.execute(query)
    return [CustomerResponse.model_validate(c) for c in result.scalars().all()]


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    result = await db.execute(select(Customer).where(Customer.customer_id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerResponse.model_validate(customer)


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    customer = Customer(**data.model_dump())
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(select(Customer).where(Customer.customer_id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
    await db.commit()
    await db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(select(Customer).where(Customer.customer_id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer.is_active = False
    await db.commit()
    return {"message": "Customer deactivated successfully"}


# ---- Finished Products ----
@router.get("/products", response_model=List[FinishedProductResponse])
async def list_finished_products(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = select(FinishedProduct).options(
        selectinload(FinishedProduct.category),
        selectinload(FinishedProduct.uom),
    )
    if search:
        query = query.where(
            FinishedProduct.product_name.ilike(f"%{search}%")
            | FinishedProduct.product_code.ilike(f"%{search}%")
        )
    if category_id:
        query = query.where(FinishedProduct.category_id == category_id)
    query = query.offset(skip).limit(limit).order_by(FinishedProduct.product_code)
    result = await db.execute(query)
    rows = result.scalars().unique().all()
    resp = []
    for p in rows:
        d = FinishedProductResponse.model_validate(p)
        d.category_name = p.category.category_name if p.category else None
        d.uom_code = p.uom.uom_code if p.uom else None
        resp.append(d)
    return resp


@router.get("/products/{product_id}", response_model=FinishedProductResponse)
async def get_finished_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    result = await db.execute(
        select(FinishedProduct)
        .options(selectinload(FinishedProduct.category), selectinload(FinishedProduct.uom))
        .where(FinishedProduct.product_id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    d = FinishedProductResponse.model_validate(product)
    d.category_name = product.category.category_name if product.category else None
    d.uom_code = product.uom.uom_code if product.uom else None
    return d


@router.put("/products/{product_id}", response_model=FinishedProductResponse)
async def update_finished_product(
    product_id: int,
    data: FinishedProductUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(
        select(FinishedProduct)
        .options(selectinload(FinishedProduct.category), selectinload(FinishedProduct.uom))
        .where(FinishedProduct.product_id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    await db.commit()
    await db.refresh(product)
    d = FinishedProductResponse.model_validate(product)
    d.category_name = product.category.category_name if product.category else None
    d.uom_code = product.uom.uom_code if product.uom else None
    return d


# ---- Dispatch ----
@router.get("", response_model=List[DispatchResponse])
async def list_dispatches(
    customer_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = select(Dispatch).options(
        selectinload(Dispatch.customer),
        selectinload(Dispatch.creator),
        selectinload(Dispatch.items).selectinload(DispatchItem.product),
    )
    if customer_id:
        query = query.where(Dispatch.customer_id == customer_id)
    if status_filter:
        query = query.where(Dispatch.delivery_status == status_filter)
    query = query.order_by(Dispatch.dispatch_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    rows = result.scalars().unique().all()
    resp = []
    for d in rows:
        dr = DispatchResponse.model_validate(d)
        dr.customer_name = d.customer.customer_name if d.customer else None
        dr.creator_name = d.creator.full_name if d.creator else None
        dr.items = []
        for item in d.items:
            di = DispatchItemResponse.model_validate(item)
            di.product_name = item.product.product_name if item.product else None
            di.product_code = item.product.product_code if item.product else None
            dr.items.append(di)
        resp.append(dr)
    return resp


@router.get("/{dispatch_id}", response_model=DispatchResponse)
async def get_dispatch(
    dispatch_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    result = await db.execute(
        select(Dispatch)
        .options(
            selectinload(Dispatch.customer),
            selectinload(Dispatch.creator),
            selectinload(Dispatch.items).selectinload(DispatchItem.product),
        )
        .where(Dispatch.dispatch_id == dispatch_id)
    )
    d = result.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    dr = DispatchResponse.model_validate(d)
    dr.customer_name = d.customer.customer_name if d.customer else None
    dr.creator_name = d.creator.full_name if d.creator else None
    dr.items = []
    for item in d.items:
        di = DispatchItemResponse.model_validate(item)
        di.product_name = item.product.product_name if item.product else None
        di.product_code = item.product.product_code if item.product else None
        dr.items.append(di)
    return dr


@router.post("", response_model=DispatchResponse, status_code=status.HTTP_201_CREATED)
async def create_dispatch(
    data: DispatchCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    items_data = data.items
    dispatch_data = data.model_dump(exclude={"items"})
    dispatch = Dispatch(**dispatch_data)
    db.add(dispatch)
    await db.flush()

    for item_data in items_data:
        di = DispatchItem(
            dispatch_id=dispatch.dispatch_id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
        )
        db.add(di)
    await db.commit()

    result = await db.execute(
        select(Dispatch)
        .options(
            selectinload(Dispatch.customer),
            selectinload(Dispatch.creator),
            selectinload(Dispatch.items).selectinload(DispatchItem.product),
        )
        .where(Dispatch.dispatch_id == dispatch.dispatch_id)
    )
    d = result.scalar_one()
    dr = DispatchResponse.model_validate(d)
    dr.customer_name = d.customer.customer_name if d.customer else None
    dr.creator_name = d.creator.full_name if d.creator else None
    dr.items = []
    for item in d.items:
        di = DispatchItemResponse.model_validate(item)
        di.product_name = item.product.product_name if item.product else None
        di.product_code = item.product.product_code if item.product else None
        dr.items.append(di)
    return dr


@router.put("/{dispatch_id}", response_model=DispatchResponse)
async def update_dispatch(
    dispatch_id: int,
    data: DispatchUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(select(Dispatch).where(Dispatch.dispatch_id == dispatch_id))
    dispatch = result.scalar_one_or_none()
    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(dispatch, key, value)
    await db.commit()
    return await get_dispatch(dispatch_id, db, _)


@router.delete("/{dispatch_id}")
async def delete_dispatch(
    dispatch_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    result = await db.execute(select(Dispatch).where(Dispatch.dispatch_id == dispatch_id))
    dispatch = result.scalar_one_or_none()
    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch not found")
    dispatch.delivery_status = "Cancelled"
    await db.commit()
    return {"message": "Dispatch cancelled"}


@router.get("/summary/recent", response_model=List[DispatchSummaryItem])
async def get_recent_dispatches(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = text("""
        SELECT
            d.dispatch_date,
            d.invoice_no,
            c.customer_name,
            d.total_amount,
            d.delivery_status,
            COUNT(di.dispatch_item_id) AS item_count
        FROM dispatch d
        JOIN customers c ON d.customer_id = c.customer_id
        LEFT JOIN dispatch_items di ON d.dispatch_id = di.dispatch_id
        WHERE d.dispatch_date >= DATE_SUB(CURDATE(), INTERVAL :days DAY)
        GROUP BY d.dispatch_id, d.dispatch_date, d.invoice_no, c.customer_name, d.total_amount, d.delivery_status
        ORDER BY d.dispatch_date DESC
        LIMIT 20
    """)
    result = await db.execute(query, {"days": days})
    rows = result.fetchall()
    return [
        DispatchSummaryItem(
            dispatch_date=str(row[0]),
            invoice_no=row[1],
            customer_name=row[2],
            total_amount=float(row[3]) if row[3] else None,
            delivery_status=row[4],
            item_count=row[5] or 0,
        )
        for row in rows
    ]
