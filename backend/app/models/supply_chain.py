from sqlalchemy import String, Integer, Boolean, Enum as SAEnum, ForeignKey, Text, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DECIMAL, TIMESTAMP
from datetime import datetime, date
from typing import Optional, List

from app.database import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    products: Mapped[List["FinishedProduct"]] = relationship("FinishedProduct", back_populates="category")


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(150), nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pincode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    gst_no: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(DECIMAL(2, 1), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    materials: Mapped[List["SupplierMaterial"]] = relationship("SupplierMaterial", back_populates="supplier")
    receipts: Mapped[List["MaterialReceipt"]] = relationship("MaterialReceipt", back_populates="supplier")


class SupplierMaterial(Base):
    __tablename__ = "supplier_materials"

    supplier_material_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("suppliers.supplier_id"), nullable=False)
    material_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_master.material_id"), nullable=False)
    unit_price: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
    quality_rating: Mapped[Optional[float]] = mapped_column(DECIMAL(2, 1), nullable=True)
    is_preferred: Mapped[bool] = mapped_column(Boolean, default=False)
    contract_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    contract_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="materials")
    material: Mapped["MaterialMaster"] = relationship("MaterialMaster")


class MaterialReceipt(Base):
    __tablename__ = "material_receipts"

    receipt_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receipt_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    supplier_id: Mapped[int] = mapped_column(Integer, ForeignKey("suppliers.supplier_id"), nullable=False)
    material_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_master.material_id"), nullable=False)
    quantity: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    unit_price: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
    invoice_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)
    received_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employees.emp_id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="receipts")
    material: Mapped["MaterialMaster"] = relationship("MaterialMaster")
    receiver: Mapped[Optional["Employee"]] = relationship("Employee")


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    material_id: Mapped[int] = mapped_column(Integer, ForeignKey("material_master.material_id"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(
        SAEnum("IN", "OUT", "ADJUSTMENT"), nullable=False
    )
    quantity: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    reference_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reference_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employees.emp_id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)

    material: Mapped["MaterialMaster"] = relationship("MaterialMaster")
    creator: Mapped[Optional["Employee"]] = relationship("Employee")


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(150), nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pincode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    gst_no: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    credit_limit: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    dispatches: Mapped[List["Dispatch"]] = relationship("Dispatch", back_populates="customer")


class FinishedProduct(Base):
    __tablename__ = "finished_products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_categories.category_id"), nullable=False)
    grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    size_spec: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    standard: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    uom_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("uom_master.uom_id"), nullable=True)
    selling_price: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
    stock_qty: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    category: Mapped["ProductCategory"] = relationship("ProductCategory", back_populates="products")
    uom: Mapped[Optional["UomMaster"]] = relationship("UomMaster")
    dispatch_items: Mapped[List["DispatchItem"]] = relationship("DispatchItem", back_populates="product")


class Dispatch(Base):
    __tablename__ = "dispatch"

    dispatch_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dispatch_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    invoice_no: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    dispatch_mode: Mapped[str] = mapped_column(
        SAEnum("Road", "Rail", "Sea"), nullable=False, default="Road"
    )
    vehicle_no: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    driver_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    total_amount: Mapped[Optional[float]] = mapped_column(DECIMAL(14, 2), nullable=True)
    delivery_status: Mapped[str] = mapped_column(
        SAEnum("Dispatched", "In Transit", "Delivered", "Cancelled"), nullable=False, default="Dispatched"
    )
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("employees.emp_id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="dispatches")
    creator: Mapped[Optional["Employee"]] = relationship("Employee")
    items: Mapped[List["DispatchItem"]] = relationship("DispatchItem", back_populates="dispatch", cascade="all, delete-orphan")


class DispatchItem(Base):
    __tablename__ = "dispatch_items"

    dispatch_item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dispatch_id: Mapped[int] = mapped_column(Integer, ForeignKey("dispatch.dispatch_id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("finished_products.product_id"), nullable=False)
    quantity: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    unit_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)

    dispatch: Mapped["Dispatch"] = relationship("Dispatch", back_populates="items")
    product: Mapped["FinishedProduct"] = relationship("FinishedProduct", back_populates="dispatch_items")
