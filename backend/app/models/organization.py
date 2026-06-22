from sqlalchemy import String, Integer, Boolean, Date, Time, Text, Enum as SAEnum, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DECIMAL
from datetime import date, time, datetime
from typing import Optional, List

from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    dept_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dept_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    dept_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dept_type: Mapped[str] = mapped_column(SAEnum("Production", "Service", "Admin"), nullable=False)
    parent_dept_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.dept_id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    children: Mapped[Optional[List["Department"]]] = relationship(
        "Department", backref="parent", remote_side="Department.dept_id"
    )


class ProductionUnit(Base):
    __tablename__ = "production_units"

    unit_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    unit_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    unit_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.dept_id"), nullable=False)
    unit_type: Mapped[str] = mapped_column(
        SAEnum("Furnace", "Converter", "Caster", "Mill", "Kiln", "Boiler", "Turbine", "Crane", "Other"),
        nullable=False,
    )
    capacity_tpa: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    department: Mapped["Department"] = relationship("Department")


class Designation(Base):
    __tablename__ = "designations"

    designation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    dept_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.dept_id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    department: Mapped[Optional["Department"]] = relationship("Department")


class ShiftMaster(Base):
    __tablename__ = "shift_masters"

    shift_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shift_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    shift_name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Employee(Base):
    __tablename__ = "employees"

    emp_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emp_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(SAEnum("M", "F", "O"), nullable=True)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.dept_id"), nullable=False)
    designation_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("designations.designation_id"), nullable=True)
    unit_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("production_units.unit_id"), nullable=True)
    shift_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("shift_masters.shift_id"), nullable=True)
    date_of_joining: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    department: Mapped["Department"] = relationship("Department")
    designation: Mapped[Optional["Designation"]] = relationship("Designation")
    unit: Mapped[Optional["ProductionUnit"]] = relationship("ProductionUnit")
    shift: Mapped[Optional["ShiftMaster"]] = relationship("ShiftMaster")


class CostCenter(Base):
    __tablename__ = "cost_centers"

    cc_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cc_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    cc_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dept_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.dept_id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    department: Mapped["Department"] = relationship("Department")
