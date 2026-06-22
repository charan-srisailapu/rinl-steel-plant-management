from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, text, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.organization import Department, ProductionUnit, Employee
from app.models.master_data import ProductCatalog, MaterialMaster, ProductionRecord, MaterialConsumption, User
from app.schemas.master_data import (
    MonthlyProductionReport, WeeklyProductionTrend, CategoryDistribution,
    CapacityUtilization, SummaryStats,
    DailyProductionItem, ShiftProductivityItem,
)
from app.models.supply_chain import FinishedProduct, Dispatch, DispatchItem, Supplier, MaterialReceipt
from app.middleware.auth import require_role, READ_ROLES

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@router.get("/summary", response_model=SummaryStats)
async def get_summary_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    dept_count = await db.scalar(select(func.count(Department.dept_id)))
    unit_count = await db.scalar(select(func.count(ProductionUnit.unit_id)))
    emp_count = await db.scalar(select(func.count(Employee.emp_id)))
    prod_count = await db.scalar(select(func.count(ProductCatalog.product_id)))
    mat_count = await db.scalar(select(func.count(MaterialMaster.material_id)))

    prod_dept = await db.scalar(
        select(func.count(Department.dept_id)).where(Department.dept_type == "Production")
    )
    svc_dept = await db.scalar(
        select(func.count(Department.dept_id)).where(Department.dept_type == "Service")
    )
    adm_dept = await db.scalar(
        select(func.count(Department.dept_id)).where(Department.dept_type == "Admin")
    )
    active_prod = await db.scalar(
        select(func.count(ProductCatalog.product_id)).where(ProductCatalog.is_active == True)
    )
    active_mat = await db.scalar(
        select(func.count(MaterialMaster.material_id)).where(MaterialMaster.is_active == True)
    )

    this_month = await db.scalar(
        select(func.coalesce(func.sum(ProductionRecord.quantity), 0)).where(
            text("DATE_FORMAT(record_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')")
        )
    )
    last_month = await db.scalar(
        select(func.coalesce(func.sum(ProductionRecord.quantity), 0)).where(
            text("DATE_FORMAT(record_date, '%Y-%m') = DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m')")
        )
    )

    return SummaryStats(
        total_departments=dept_count or 0,
        total_units=unit_count or 0,
        total_employees=emp_count or 0,
        total_products=prod_count or 0,
        total_materials=mat_count or 0,
        production_depts=prod_dept or 0,
        service_depts=svc_dept or 0,
        admin_depts=adm_dept or 0,
        active_products=active_prod or 0,
        active_materials=active_mat or 0,
        this_month_production=float(this_month) if this_month else None,
        last_month_production=float(last_month) if last_month else None,
    )


@router.get("/production/monthly", response_model=List[MonthlyProductionReport])
async def get_monthly_production(
    months: int = Query(6, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = text("""
        SELECT
            MONTHNAME(MIN(pr.record_date)) AS month,
            YEAR(MIN(pr.record_date)) AS year,
            pc.product_category AS category,
            SUM(pr.quantity) AS total_quantity,
            SUM(COALESCE(pr.target_quantity, 0)) AS total_target,
            COUNT(*) AS record_count
        FROM production_records pr
        JOIN product_catalog pc ON pr.product_id = pc.product_id
        WHERE pr.record_date >= DATE_SUB(CURDATE(), INTERVAL :months MONTH)
        GROUP BY YEAR(pr.record_date), MONTH(pr.record_date), pc.product_category
        ORDER BY year DESC, MONTH(pr.record_date) DESC, category
    """)
    result = await db.execute(query, {"months": months})
    rows = result.fetchall()

    return [
        MonthlyProductionReport(
            month=row[0],
            year=row[1],
            category=row[2],
            total_quantity=float(row[3]),
            total_target=float(row[4]) if row[4] else None,
            achievement_pct=round(float(row[3]) / float(row[4]) * 100, 1) if row[4] and float(row[4]) > 0 else None,
            record_count=row[5],
        )
        for row in rows
    ]


@router.get("/production/weekly", response_model=List[WeeklyProductionTrend])
async def get_weekly_trend(
    weeks: int = Query(12, ge=4, le=52),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = text("""
        SELECT
            DATE_SUB(pr.record_date, INTERVAL WEEKDAY(pr.record_date) DAY) AS week_start,
            pc.product_category,
            SUM(pr.quantity) AS total_quantity
        FROM production_records pr
        JOIN product_catalog pc ON pr.product_id = pc.product_id
        WHERE pr.record_date >= DATE_SUB(CURDATE(), INTERVAL :weeks WEEK)
        GROUP BY DATE_SUB(pr.record_date, INTERVAL WEEKDAY(pr.record_date) DAY), pc.product_category
        ORDER BY week_start ASC, pc.product_category
    """)
    result = await db.execute(query, {"weeks": weeks})
    rows = result.fetchall()

    from datetime import timedelta as td
    return [
        WeeklyProductionTrend(
            week_start=str(row[0]),
            week_end=str(row[0] + td(days=6)),
            product_category=row[1],
            total_quantity=float(row[2]),
        )
        for row in rows
    ]


@router.get("/production/by-category", response_model=List[CategoryDistribution])
async def get_production_by_category(
    months: int = Query(6, ge=1, le=24),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = text("""
        SELECT
            pc.product_category,
            SUM(pr.quantity) AS total_qty,
            SUM(pr.quantity) * 100.0 / SUM(SUM(pr.quantity)) OVER () AS pct
        FROM production_records pr
        JOIN product_catalog pc ON pr.product_id = pc.product_id
        WHERE pr.record_date >= DATE_SUB(CURDATE(), INTERVAL :months MONTH)
        GROUP BY pc.product_category
        ORDER BY total_qty DESC
    """)
    result = await db.execute(query, {"months": months})
    rows = result.fetchall()
    total = sum(row[1] for row in rows) or 1

    return [
        CategoryDistribution(category=row[0], count=int(row[1]), percentage=round(row[2], 1))
        for row in rows
    ]


@router.get("/production/capacity", response_model=List[CapacityUtilization])
async def get_capacity_utilization(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = text("""
        SELECT
            pu.unit_name,
            pu.unit_code,
            pu.capacity_tpa,
            COALESCE(SUM(pr.quantity), 0) AS actual_production
        FROM production_units pu
        LEFT JOIN production_records pr ON pu.unit_id = pr.unit_id
            AND pr.record_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY pu.unit_id, pu.unit_name, pu.unit_code, pu.capacity_tpa
        ORDER BY pu.unit_code
    """)
    result = await db.execute(query)
    rows = result.fetchall()

    return [
        CapacityUtilization(
            unit_name=row[0],
            unit_code=row[1],
            capacity_tpa=float(row[2]) if row[2] else None,
            actual_production=float(row[3]),
            utilization_pct=round(float(row[3]) / float(row[2]) * 100, 1)
            if row[2] and float(row[2]) > 0 else None,
        )
        for row in rows
    ]


@router.get("/master/departments", response_model=List[CategoryDistribution])
async def get_dept_distribution(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    result = await db.execute(
        select(Department.dept_type, func.count(Department.dept_id).label("count"))
        .group_by(Department.dept_type)
        .order_by(text("count DESC"))
    )
    rows = result.fetchall()
    total = sum(row[1] for row in rows) or 1
    return [
        CategoryDistribution(category=row[0], count=row[1], percentage=round(row[1] / total * 100, 1))
        for row in rows
    ]


@router.get("/master/employees-by-dept", response_model=List[CategoryDistribution])
async def get_employees_by_dept(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    result = await db.execute(
        select(Department.dept_code, func.count(Employee.emp_id).label("count"))
        .join(Employee, Employee.dept_id == Department.dept_id)
        .group_by(Department.dept_code)
        .order_by(text("count DESC"))
    )
    rows = result.fetchall()
    total = sum(row[1] for row in rows) or 1
    return [
        CategoryDistribution(category=row[0], count=row[1], percentage=round(row[1] / total * 100, 1))
        for row in rows
    ]


@router.get("/master/products-by-category", response_model=List[CategoryDistribution])
async def get_products_by_category(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    result = await db.execute(
        select(ProductCatalog.product_category, func.count(ProductCatalog.product_id).label("count"))
        .group_by(ProductCatalog.product_category)
        .order_by(text("count DESC"))
    )
    rows = result.fetchall()
    total = sum(row[1] for row in rows) or 1
    return [
        CategoryDistribution(category=row[0], count=row[1], percentage=round(row[1] / total * 100, 1))
        for row in rows
    ]


@router.get("/master/materials-by-type", response_model=List[CategoryDistribution])
async def get_materials_by_type(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    result = await db.execute(
        select(MaterialMaster.material_type, func.count(MaterialMaster.material_id).label("count"))
        .group_by(MaterialMaster.material_type)
        .order_by(text("count DESC"))
    )
    rows = result.fetchall()
    total = sum(row[1] for row in rows) or 1
    return [
        CategoryDistribution(category=row[0], count=row[1], percentage=round(row[1] / total * 100, 1))
        for row in rows
    ]


@router.get("/master/units-by-type", response_model=List[CategoryDistribution])
async def get_units_by_type(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    result = await db.execute(
        select(ProductionUnit.unit_type, func.count(ProductionUnit.unit_id).label("count"))
        .group_by(ProductionUnit.unit_type)
        .order_by(text("count DESC"))
    )
    rows = result.fetchall()
    total = sum(row[1] for row in rows) or 1
    return [
        CategoryDistribution(category=row[0], count=row[1], percentage=round(row[1] / total * 100, 1))
        for row in rows
    ]


@router.get("/production/daily", response_model=List[DailyProductionItem])
async def get_daily_production(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = text("""
        SELECT
            pr.record_date,
            pc.product_category,
            SUM(pr.quantity) AS total_quantity
        FROM production_records pr
        JOIN product_catalog pc ON pr.product_id = pc.product_id
        WHERE pr.record_date >= DATE_SUB(CURDATE(), INTERVAL :days DAY)
        GROUP BY pr.record_date, pc.product_category
        ORDER BY pr.record_date ASC, pc.product_category
    """)
    result = await db.execute(query, {"days": days})
    rows = result.fetchall()
    return [
        DailyProductionItem(
            record_date=str(row[0]),
            product_category=row[1],
            total_quantity=float(row[2]),
        )
        for row in rows
    ]


@router.get("/production/shift-productivity", response_model=List[ShiftProductivityItem])
async def get_shift_productivity(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = text("""
        SELECT
            sm.shift_code,
            sm.shift_name,
            COALESCE(SUM(pr.quantity), 0) AS total_quantity,
            COUNT(pr.record_id) AS record_count
        FROM shift_masters sm
        LEFT JOIN employees e ON sm.shift_id = e.shift_id
        LEFT JOIN production_records pr ON e.emp_id = pr.record_id
            AND pr.record_date >= DATE_SUB(CURDATE(), INTERVAL :days DAY)
        GROUP BY sm.shift_id, sm.shift_code, sm.shift_name
        ORDER BY total_quantity DESC
    """)
    result = await db.execute(query, {"days": days})
    rows = result.fetchall()
    return [
        ShiftProductivityItem(
            shift_code=row[0],
            shift_name=row[1],
            total_quantity=float(row[2]),
            record_count=row[3] or 0,
            avg_quantity=round(float(row[2]) / row[3], 2) if row[3] and row[3] > 0 else None,
        )
        for row in rows
    ]


@router.get("/inventory/summary")
async def get_inventory_summary(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    result = await db.execute(
        select(
            MaterialMaster.material_type,
            func.count(MaterialMaster.material_id).label("count"),
        )
        .group_by(MaterialMaster.material_type)
    )
    rows = result.fetchall()
    return [
        {
            "material_type": row[0],
            "count": row[1],
        }
        for row in rows
    ]


@router.get("/dispatch/daily-count")
async def get_dispatch_daily_count(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = text("""
        SELECT
            d.dispatch_date,
            d.delivery_status,
            COUNT(*) AS dispatch_count,
            COALESCE(SUM(d.total_amount), 0) AS total_amount
        FROM dispatch d
        WHERE d.dispatch_date >= DATE_SUB(CURDATE(), INTERVAL :days DAY)
        GROUP BY d.dispatch_date, d.delivery_status
        ORDER BY d.dispatch_date ASC
    """)
    result = await db.execute(query, {"days": days})
    rows = result.fetchall()
    return [
        {
            "dispatch_date": str(row[0]),
            "delivery_status": row[1],
            "dispatch_count": row[2],
            "total_amount": float(row[3]),
        }
        for row in rows
    ]


@router.get("/product-stock")
async def get_product_stock(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(READ_ROLES)),
):
    query = text("""
        SELECT
            fp.product_code,
            fp.product_name,
            pc.category_name,
            fp.stock_qty,
            u.uom_code,
            fp.selling_price
        FROM finished_products fp
        JOIN product_categories pc ON fp.category_id = pc.category_id
        LEFT JOIN uom_master u ON fp.uom_id = u.uom_id
        WHERE fp.is_active = TRUE
        ORDER BY fp.stock_qty DESC
    """)
    result = await db.execute(query)
    rows = result.fetchall()
    return [
        {
            "product_code": row[0],
            "product_name": row[1],
            "category_name": row[2],
            "stock_qty": float(row[3]),
            "uom_code": row[4],
            "selling_price": float(row[5]) if row[5] else None,
        }
        for row in rows
    ]
