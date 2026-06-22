from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, time


# ---- Department ----
class DepartmentBase(BaseModel):
    dept_code: str
    dept_name: str
    dept_type: str = "Production"
    parent_dept_id: Optional[int] = None
    is_active: bool = True


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    dept_code: Optional[str] = None
    dept_name: Optional[str] = None
    dept_type: Optional[str] = None
    parent_dept_id: Optional[int] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    dept_id: int
    dept_code: str
    dept_name: str
    dept_type: str
    parent_dept_id: Optional[int] = None
    is_active: bool


class DepartmentTreeResponse(DepartmentResponse):
    children: Optional[List["DepartmentTreeResponse"]] = None


# ---- ProductionUnit ----
class ProductionUnitBase(BaseModel):
    unit_code: str
    unit_name: str
    dept_id: int
    unit_type: str = "Other"
    capacity_tpa: Optional[float] = None
    is_active: bool = True


class ProductionUnitCreate(ProductionUnitBase):
    pass


class ProductionUnitUpdate(BaseModel):
    unit_code: Optional[str] = None
    unit_name: Optional[str] = None
    dept_id: Optional[int] = None
    unit_type: Optional[str] = None
    capacity_tpa: Optional[float] = None
    is_active: Optional[bool] = None


class ProductionUnitResponse(ProductionUnitBase):
    model_config = ConfigDict(from_attributes=True)

    unit_id: int


# ---- Designation ----
class DesignationBase(BaseModel):
    title: str
    grade: Optional[str] = None
    dept_id: Optional[int] = None
    is_active: bool = True


class DesignationCreate(DesignationBase):
    pass


class DesignationUpdate(BaseModel):
    title: Optional[str] = None
    grade: Optional[str] = None
    dept_id: Optional[int] = None
    is_active: Optional[bool] = None


class DesignationResponse(DesignationBase):
    model_config = ConfigDict(from_attributes=True)

    designation_id: int


# ---- ShiftMaster ----
class ShiftMasterBase(BaseModel):
    shift_code: str
    shift_name: str
    start_time: time
    end_time: time
    description: Optional[str] = None
    is_active: bool = True


class ShiftMasterCreate(ShiftMasterBase):
    pass


class ShiftMasterUpdate(BaseModel):
    shift_code: Optional[str] = None
    shift_name: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ShiftMasterResponse(ShiftMasterBase):
    model_config = ConfigDict(from_attributes=True)

    shift_id: int


# ---- Employee ----
class EmployeeBase(BaseModel):
    emp_number: str
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    dept_id: int
    designation_id: Optional[int] = None
    unit_id: Optional[int] = None
    shift_id: Optional[int] = None
    date_of_joining: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    emp_number: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    dept_id: Optional[int] = None
    designation_id: Optional[int] = None
    unit_id: Optional[int] = None
    shift_id: Optional[int] = None
    date_of_joining: Optional[date] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    emp_id: int


# ---- CostCenter ----
class CostCenterBase(BaseModel):
    cc_code: str
    cc_name: str
    dept_id: int
    is_active: bool = True


class CostCenterCreate(CostCenterBase):
    pass


class CostCenterUpdate(BaseModel):
    cc_code: Optional[str] = None
    cc_name: Optional[str] = None
    dept_id: Optional[int] = None
    is_active: Optional[bool] = None


class CostCenterResponse(CostCenterBase):
    model_config = ConfigDict(from_attributes=True)

    cc_id: int
