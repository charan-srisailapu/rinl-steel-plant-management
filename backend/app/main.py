import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, departments, employees, products, materials, units, uom, reports
from app.routers import suppliers, inventory, dispatch, product_categories


@asynccontextmanager
async def lifespan(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="RINL Steel Plant - Centralized Database API",
    description="Smart Steel Plant Management & Analytics System",
    version="2.0.0",
    lifespan=lifespan,
)

allow_origins_env = os.getenv("CORS_ORIGINS")
if not allow_origins_env:
    if os.getenv("RENDER") or os.getenv("RAILWAY") or os.getenv("VERCEL"):
        raise RuntimeError("CORS_ORIGINS environment variable is required on deployment platforms")
    allow_origins_env = "http://localhost:5173,http://localhost:3000"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins_env.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(employees.router)
app.include_router(products.router)
app.include_router(materials.router)
app.include_router(units.router)
app.include_router(uom.router)
app.include_router(reports.router)
app.include_router(suppliers.router)
app.include_router(inventory.router)
app.include_router(dispatch.router)
app.include_router(product_categories.router)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "module": "Phase 2 - Full System"}
