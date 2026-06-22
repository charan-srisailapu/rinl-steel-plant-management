from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.master_data import User, MaterialMaster
from app.models.supply_chain import InventoryTransaction, MaterialReceipt
from app.schemas.master_data import (
    InventoryTransactionCreate, InventoryTransactionResponse,
    StockStatusItem,
)
from app.middleware.auth import get_current_user, require_role, WRITE_ROLES, READ_ROLES

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])


@router.get("/stock", response_model=List[StockStatusItem])
async def get_stock_status(
    reorder_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = text("""
        SELECT
            m.material_id,
            m.material_code,
            m.material_name,
            m.material_type,
            u.uom_code,
            COALESCE(SUM(CASE WHEN it.transaction_type = 'IN' THEN it.quantity ELSE 0 END), 0) AS total_received,
            COALESCE(SUM(CASE WHEN it.transaction_type = 'OUT' THEN it.quantity ELSE 0 END), 0) AS total_consumed,
            COALESCE(SUM(CASE WHEN it.transaction_type = 'IN' THEN it.quantity ELSE 0 END), 0)
            - COALESCE(SUM(CASE WHEN it.transaction_type = 'OUT' THEN it.quantity ELSE 0 END), 0) AS net_stock,
            m.reorder_level
        FROM material_master m
        LEFT JOIN uom_master u ON m.uom_id = u.uom_id
        LEFT JOIN inventory_transactions it ON m.material_id = it.material_id
        WHERE m.is_active = TRUE
        GROUP BY m.material_id, m.material_code, m.material_name, m.material_type, u.uom_code, m.reorder_level
        ORDER BY net_stock ASC
    """)
    result = await db.execute(query)
    rows = result.fetchall()
    items = []
    for row in rows:
        net_stock = float(row[7])
        reorder_level = float(row[8]) if row[8] else None
        status_label = "OK"
        if reorder_level is not None and net_stock <= reorder_level:
            status_label = "REORDER"
        elif reorder_level is not None and net_stock <= reorder_level * 1.2:
            status_label = "LOW"
        item = StockStatusItem(
            material_id=row[0],
            material_code=row[1],
            material_name=row[2],
            material_type=row[3],
            uom_code=row[4],
            total_received=float(row[5]),
            total_consumed=float(row[6]),
            net_stock=net_stock,
            reorder_level=reorder_level,
            status=status_label,
        )
        if reorder_only and status_label != "REORDER":
            continue
        items.append(item)
    return items


@router.get("/transactions", response_model=List[InventoryTransactionResponse])
async def list_transactions(
    material_id: Optional[int] = Query(None),
    transaction_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = select(InventoryTransaction).options(
        selectinload(InventoryTransaction.material),
        selectinload(InventoryTransaction.creator),
    )
    if material_id:
        query = query.where(InventoryTransaction.material_id == material_id)
    if transaction_type:
        query = query.where(InventoryTransaction.transaction_type == transaction_type)
    query = query.order_by(InventoryTransaction.transaction_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    rows = result.scalars().unique().all()
    resp = []
    for t in rows:
        d = InventoryTransactionResponse.model_validate(t)
        d.material_name = t.material.material_name if t.material else None
        d.creator_name = t.creator.full_name if t.creator else None
        resp.append(d)
    return resp


@router.post("/transactions", response_model=InventoryTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: InventoryTransactionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(WRITE_ROLES)),
):
    txn = InventoryTransaction(**data.model_dump())
    db.add(txn)
    await db.commit()
    await db.refresh(txn)
    result = await db.execute(
        select(InventoryTransaction)
        .options(selectinload(InventoryTransaction.material), selectinload(InventoryTransaction.creator))
        .where(InventoryTransaction.transaction_id == txn.transaction_id)
    )
    t = result.scalar_one()
    d = InventoryTransactionResponse.model_validate(t)
    d.material_name = t.material.material_name if t.material else None
    d.creator_name = t.creator.full_name if t.creator else None
    return d


@router.get("/reorder-items", response_model=List[StockStatusItem])
async def get_reorder_items(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    return await get_stock_status(reorder_only=True, db=db, _=_)


@router.get("/receipts/summary")
async def get_receipts_summary(
    months: int = Query(6, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = text("""
        SELECT
            DATE_FORMAT(mr.receipt_date, '%Y-%m') AS month,
            m.material_type,
            COUNT(*) AS receipt_count,
            SUM(mr.quantity) AS total_qty,
            AVG(mr.unit_price) AS avg_price
        FROM material_receipts mr
        JOIN material_master m ON mr.material_id = m.material_id
        WHERE mr.receipt_date >= DATE_SUB(CURDATE(), INTERVAL :months MONTH)
        GROUP BY DATE_FORMAT(mr.receipt_date, '%Y-%m'), m.material_type
        ORDER BY month DESC, m.material_type
    """)
    result = await db.execute(query, {"months": months})
    rows = result.fetchall()
    return [
        {
            "month": row[0],
            "material_type": row[1],
            "receipt_count": row[2],
            "total_qty": float(row[3]),
            "avg_price": float(row[4]) if row[4] else None,
        }
        for row in rows
    ]
