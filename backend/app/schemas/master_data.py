from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime


# ---- UomMaster ----
class UomMasterBase(BaseModel):
    uom_code: str
    uom_name: str
    is_active: bool = True


class UomMasterCreate(UomMasterBase):
    pass


class UomMasterUpdate(BaseModel):
    uom_code: Optional[str] = None
    uom_name: Optional[str] = None
    is_active: Optional[bool] = None


class UomMasterResponse(UomMasterBase):
    model_config = ConfigDict(from_attributes=True)

    uom_id: int


# ---- ProductCatalog ----
class ProductCatalogBase(BaseModel):
    product_code: str
    product_name: str
    product_category: str = "Long"
    product_group: Optional[str] = None
    grade: Optional[str] = None
    size_spec: Optional[str] = None
    uom_id: Optional[int] = None
    standard: Optional[str] = None
    is_active: bool = True


class ProductCatalogCreate(ProductCatalogBase):
    pass


class ProductCatalogUpdate(BaseModel):
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    product_category: Optional[str] = None
    product_group: Optional[str] = None
    grade: Optional[str] = None
    size_spec: Optional[str] = None
    uom_id: Optional[int] = None
    standard: Optional[str] = None
    is_active: Optional[bool] = None


class ProductCatalogResponse(ProductCatalogBase):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    uom: Optional[UomMasterResponse] = None


# ---- MaterialMaster ----
class MaterialMasterBase(BaseModel):
    material_code: str
    material_name: str
    material_type: str = "Raw"
    material_group: Optional[str] = None
    uom_id: Optional[int] = None
    reorder_level: Optional[float] = None
    lead_time_days: Optional[int] = None
    is_active: bool = True


class MaterialMasterCreate(MaterialMasterBase):
    pass


class MaterialMasterUpdate(BaseModel):
    material_code: Optional[str] = None
    material_name: Optional[str] = None
    material_type: Optional[str] = None
    material_group: Optional[str] = None
    uom_id: Optional[int] = None
    reorder_level: Optional[float] = None
    lead_time_days: Optional[int] = None
    is_active: Optional[bool] = None


class MaterialMasterResponse(MaterialMasterBase):
    model_config = ConfigDict(from_attributes=True)

    material_id: int
    uom: Optional[UomMasterResponse] = None


# ---- User ----
class UserBase(BaseModel):
    emp_id: int
    username: str
    role: str = "report_viewer"
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    last_login: Optional[datetime] = None


# ---- Auth ----
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ---- Reports ----
class MonthlyProductionReport(BaseModel):
    month: str
    year: int
    category: str
    total_quantity: float
    total_target: Optional[float] = None
    achievement_pct: Optional[float] = None
    record_count: int


class WeeklyProductionTrend(BaseModel):
    week_start: str
    week_end: str
    total_quantity: float
    product_category: str


class CategoryDistribution(BaseModel):
    category: str
    count: int
    percentage: float


class CapacityUtilization(BaseModel):
    unit_name: str
    unit_code: str
    capacity_tpa: Optional[float] = None
    actual_production: float
    utilization_pct: Optional[float] = None


class SummaryStats(BaseModel):
    total_departments: int
    total_units: int
    total_employees: int
    total_products: int
    total_materials: int
    production_depts: int
    service_depts: int
    admin_depts: int
    active_products: int
    active_materials: int
    this_month_production: Optional[float] = None
    last_month_production: Optional[float] = None


# ---- ProductCategory ----
class ProductCategoryBase(BaseModel):
    category_name: str
    description: Optional[str] = None


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    description: Optional[str] = None


class ProductCategoryResponse(ProductCategoryBase):
    model_config = ConfigDict(from_attributes=True)
    category_id: int


# ---- Supplier ----
class SupplierBase(BaseModel):
    supplier_code: str
    supplier_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    gst_no: Optional[str] = None
    rating: Optional[float] = None
    is_active: bool = True


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    supplier_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    gst_no: Optional[str] = None
    rating: Optional[float] = None
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    model_config = ConfigDict(from_attributes=True)
    supplier_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---- SupplierMaterial ----
class SupplierMaterialBase(BaseModel):
    supplier_id: int
    material_id: int
    unit_price: Optional[float] = None
    quality_rating: Optional[float] = None
    is_preferred: bool = False
    contract_start: Optional[str] = None
    contract_end: Optional[str] = None


class SupplierMaterialCreate(SupplierMaterialBase):
    pass


class SupplierMaterialResponse(SupplierMaterialBase):
    model_config = ConfigDict(from_attributes=True)
    supplier_material_id: int
    supplier_name: Optional[str] = None
    material_name: Optional[str] = None


# ---- MaterialReceipt ----
class MaterialReceiptBase(BaseModel):
    receipt_date: date
    supplier_id: int
    material_id: int
    quantity: float
    unit_price: Optional[float] = None
    invoice_no: Optional[str] = None
    quality_score: Optional[float] = None
    received_by: Optional[int] = None
    notes: Optional[str] = None


class MaterialReceiptCreate(MaterialReceiptBase):
    pass


class MaterialReceiptResponse(MaterialReceiptBase):
    model_config = ConfigDict(from_attributes=True)
    receipt_id: int
    created_at: Optional[datetime] = None
    supplier_name: Optional[str] = None
    material_name: Optional[str] = None
    receiver_name: Optional[str] = None


# ---- InventoryTransaction ----
class InventoryTransactionBase(BaseModel):
    transaction_date: date
    material_id: int
    transaction_type: str
    quantity: float
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    remarks: Optional[str] = None
    created_by: Optional[int] = None


class InventoryTransactionCreate(InventoryTransactionBase):
    pass


class InventoryTransactionResponse(InventoryTransactionBase):
    model_config = ConfigDict(from_attributes=True)
    transaction_id: int
    created_at: Optional[datetime] = None
    material_name: Optional[str] = None
    creator_name: Optional[str] = None


# ---- Customer ----
class CustomerBase(BaseModel):
    customer_code: str
    customer_name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    gst_no: Optional[str] = None
    credit_limit: Optional[float] = None
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    gst_no: Optional[str] = None
    credit_limit: Optional[float] = None
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)
    customer_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---- FinishedProduct ----
class FinishedProductBase(BaseModel):
    product_code: str
    product_name: str
    category_id: int
    grade: Optional[str] = None
    size_spec: Optional[str] = None
    standard: Optional[str] = None
    uom_id: Optional[int] = None
    selling_price: Optional[float] = None
    stock_qty: float = 0
    is_active: bool = True


class FinishedProductCreate(FinishedProductBase):
    pass


class FinishedProductUpdate(BaseModel):
    product_name: Optional[str] = None
    category_id: Optional[int] = None
    grade: Optional[str] = None
    size_spec: Optional[str] = None
    standard: Optional[str] = None
    uom_id: Optional[int] = None
    selling_price: Optional[float] = None
    stock_qty: Optional[float] = None
    is_active: Optional[bool] = None


class FinishedProductResponse(FinishedProductBase):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    category_name: Optional[str] = None
    uom_code: Optional[str] = None


# ---- Dispatch ----
class DispatchItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit_price: float


class DispatchItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    dispatch_item_id: int
    dispatch_id: int
    product_id: int
    quantity: float
    unit_price: float
    total_price: Optional[float] = None
    product_name: Optional[str] = None
    product_code: Optional[str] = None


class DispatchBase(BaseModel):
    dispatch_date: date
    customer_id: int
    invoice_no: str
    dispatch_mode: str = "Road"
    vehicle_no: Optional[str] = None
    driver_name: Optional[str] = None
    total_amount: Optional[float] = None
    delivery_status: str = "Dispatched"
    created_by: Optional[int] = None
    notes: Optional[str] = None


class DispatchCreate(DispatchBase):
    items: List[DispatchItemCreate]


class DispatchUpdate(BaseModel):
    dispatch_date: Optional[date] = None
    customer_id: Optional[int] = None
    dispatch_mode: Optional[str] = None
    vehicle_no: Optional[str] = None
    driver_name: Optional[str] = None
    total_amount: Optional[float] = None
    delivery_status: Optional[str] = None
    notes: Optional[str] = None


class DispatchResponse(DispatchBase):
    model_config = ConfigDict(from_attributes=True)
    dispatch_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    customer_name: Optional[str] = None
    creator_name: Optional[str] = None
    items: List[DispatchItemResponse] = []


# ---- Inventory Stock Status ----
class StockStatusItem(BaseModel):
    material_id: int
    material_code: str
    material_name: str
    material_type: str
    uom_code: Optional[str] = None
    total_received: float
    total_consumed: float
    net_stock: float
    reorder_level: Optional[float] = None
    status: str = "OK"


# ---- Supplier Performance ----
class SupplierPerformanceItem(BaseModel):
    supplier_id: int
    supplier_code: str
    supplier_name: str
    total_receipts: int
    total_quantity: float
    avg_quality_score: Optional[float] = None
    avg_unit_price: Optional[float] = None
    rating: Optional[float] = None


# ---- Shift Productivity ----
class ShiftProductivityItem(BaseModel):
    shift_code: str
    shift_name: str
    total_quantity: float
    record_count: int
    avg_quantity: Optional[float] = None


# ---- Daily Production ----
class DailyProductionItem(BaseModel):
    record_date: date
    product_category: str
    total_quantity: float


# ---- Dispatch Summary ----
class DispatchSummaryItem(BaseModel):
    dispatch_date: date
    invoice_no: str
    customer_name: str
    total_amount: Optional[float] = None
    delivery_status: str
    item_count: int
