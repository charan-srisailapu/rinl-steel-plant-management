from sqlalchemy import String, Integer, Boolean, Enum as SAEnum, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DECIMAL, TIMESTAMP
from datetime import datetime, date
from typing import Optional

from app.database import Base


class UomMaster(Base):
    __tablename__ = "uom_master"

    uom_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uom_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    uom_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ProductCatalog(Base):
    __tablename__ = "product_catalog"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    product_category: Mapped[str] = mapped_column(
        SAEnum("Semis", "Long", "Flat", "ByProduct", "Service"), nullable=False
    )
    product_group: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    size_spec: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    uom_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("uom_master.uom_id"), nullable=True)
    standard: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    uom: Mapped[Optional["UomMaster"]] = relationship("UomMaster")


class MaterialMaster(Base):
    __tablename__ = "material_master"

    material_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    material_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    material_name: Mapped[str] = mapped_column(String(100), nullable=False)
    material_type: Mapped[str] = mapped_column(
        SAEnum("Raw", "Consumable", "Spare", "Fuel", "Refractory", "Chemical", "Packaging"),
        nullable=False,
    )
    material_group: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    uom_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("uom_master.uom_id"), nullable=True)
    reorder_level: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)
    lead_time_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    uom: Mapped[Optional["UomMaster"]] = relationship("UomMaster")


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.emp_id"), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        SAEnum("admin", "production", "qa", "commercial", "maintenance", "hr", "finance", "report_viewer"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)

    employee: Mapped["Employee"] = relationship("Employee")


class ProductionRecord(Base):
    __tablename__ = "production_records"

    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_catalog.product_id"), nullable=False)
    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("production_units.unit_id"), nullable=False)
    quantity: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    target_quantity: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)
    yield_percent: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)

    product: Mapped["ProductCatalog"] = relationship("ProductCatalog")
    unit: Mapped["ProductionUnit"] = relationship("ProductionUnit")


class MaterialConsumption(Base):
    __tablename__ = "material_consumption"

    consumption_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    material_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_master.material_id"), nullable=False)
    unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("production_units.unit_id"), nullable=False)
    quantity: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)

    material: Mapped["MaterialMaster"] = relationship("MaterialMaster")
    unit: Mapped["ProductionUnit"] = relationship("ProductionUnit")
