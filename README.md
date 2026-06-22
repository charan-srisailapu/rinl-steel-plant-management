# RINL Steel Plant - Smart Steel Plant Management & Analytics System

A full-stack DBMS project for managing operations of a steel plant, built with **FastAPI + React + MySQL**.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Ant Design 5, Recharts, Axios |
| Backend | FastAPI, SQLAlchemy 2.0 (async), Pydantic v2 |
| Database | MySQL 8.0 with strict mode |
| Auth | JWT tokens |

## Features

- **Organization Management** — Departments, Designations, Production Units, Shifts
- **Master Data** — Employees, Materials, Products, UOM
- **Supplier Management** — Supplier CRUD, material mappings, receipts, performance tracking
- **Raw Material Inventory** — Stock status with reorder alerts, transaction log
- **Production Management** — Daily production records, shift productivity, capacity reports
- **Employee Management** — Employee directory with department/unit/shift assignments
- **Finished Products** — Product catalog with stock & selling price management
- **Dispatch Management** — Customer CRUD, dispatch creation with line items, status tracking
- **Analytics & Reports** — Summary dashboard, production charts, inventory analytics, supplier performance

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0

### Database
```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/schema_extension.sql
```

### Backend
```bash
cd backend
pip install -r requirements.txt
python setup_db.py           # Initialize base data
python seed_extension.py     # Seed extended tables
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Login
- Username: `a` | Password: `admin123` (admin)
- Available users: `a`, `b`, `d`, `j` (all with `admin123`)

## API Endpoints

| Prefix | Module |
|--------|--------|
| `/api/v1/auth` | Login, current user |
| `/api/v1/departments` | Department CRUD + tree |
| `/api/v1/employees` | Employee CRUD |
| `/api/v1/products` | Product catalog |
| `/api/v1/materials` | Material master |
| `/api/v1/suppliers` | Suppliers, materials, receipts, performance |
| `/api/v1/inventory` | Stock status, transactions, reorder alerts |
| `/api/v1/dispatch` | Customers, finished products, dispatch CRUD |
| `/api/v1/product-categories` | Product categories |
| `/api/v1/reports` | Summary, production, inventory, dispatch reports |
