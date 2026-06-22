"""
Run this script to initialize the database and seed data.
Usage: python setup_db.py
"""

import asyncio
import bcrypt
import random
from datetime import time as dt_time, date as dt_date, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.config import settings
from app.database import Base
from app.models.organization import Department, ProductionUnit, Designation, ShiftMaster, Employee, CostCenter
from app.models.master_data import UomMaster, ProductCatalog, MaterialMaster, User, ProductionRecord, MaterialConsumption

PASSWORD = "admin123"


async def setup():
    # Create engine without database to create DB first
    base_url = settings.database_url.rsplit("/", 1)[0]
    engine_no_db = create_async_engine(base_url + "/mysql", isolation_level="AUTOCOMMIT")

    async with engine_no_db.connect() as conn:
        result = await conn.execute(
            text("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'rinl_steel_plant'")
        )
        if not result.scalar():
            await conn.execute(text("CREATE DATABASE rinl_steel_plant CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            print("Created database 'rinl_steel_plant'")
        else:
            print("Database 'rinl_steel_plant' already exists")
    await engine_no_db.dispose()

    # Now connect to the actual database
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created/verified")

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # Check if already seeded (check production_records to detect partial seed)
        result = await session.execute(text("SELECT COUNT(*) FROM production_records"))
        if result.scalar() > 0:
            print("Database already has production records. Skipping seed.")
            await engine.dispose()
            return

        # UOM
        uoms = [
            UomMaster(uom_code="MT", uom_name="Metric Tonne"),
            UomMaster(uom_code="KG", uom_name="Kilogram"),
            UomMaster(uom_code="L", uom_name="Litre"),
            UomMaster(uom_code="KL", uom_name="Kilolitre"),
            UomMaster(uom_code="NOS", uom_name="Numbers"),
            UomMaster(uom_code="M", uom_name="Metre"),
            UomMaster(uom_code="MM", uom_name="Millimetre"),
            UomMaster(uom_code="KWH", uom_name="Kilowatt Hour"),
            UomMaster(uom_code="SCM", uom_name="Standard Cubic Metre"),
            UomMaster(uom_code="PAX", uom_name="Person / Headcount"),
        ]
        session.add_all(uoms)
        await session.flush()
        print("Seeded UOMs")

        # Departments
        depts_data = [
            ("MGMT", "Management", "Admin", None),
            ("PROD", "Production Division", "Production", None),
            ("SRV", "Services Division", "Service", None),
            ("ADM", "Administration", "Admin", None),
            ("RMHP", "Raw Material Handling Plant", "Production", "PROD"),
            ("COCCP", "Coke Oven & Coal Chemical Plant", "Production", "PROD"),
            ("SP", "Sinter Plant", "Production", "PROD"),
            ("CRMP", "Calcining & Refractory Material Plant", "Production", "PROD"),
            ("BF", "Blast Furnace", "Production", "PROD"),
            ("SMS", "Steel Melting Shop", "Production", "PROD"),
            ("CCD", "Continuous Casting Department", "Production", "PROD"),
            ("LMMM", "Light & Medium Merchant Mill", "Production", "PROD"),
            ("MMSM", "Medium Merchant & Structural Mill", "Production", "PROD"),
            ("WRM", "Wire Rod Mill", "Production", "PROD"),
            ("RSRS", "Roll Shop & Repair Shop", "Production", "PROD"),
            ("TPP", "Thermal Power Plant", "Service", "SRV"),
            ("WMD", "Water Management Department", "Service", "SRV"),
            ("QATD", "Quality Assurance & Technology Development", "Service", "SRV"),
            ("CME", "Central Maintenance - Electrical", "Service", "SRV"),
            ("CMM", "Central Maintenance - Mechanical", "Service", "SRV"),
            ("CED", "Civil Engineering Department", "Service", "SRV"),
            ("EMD", "Energy Management Department", "Service", "SRV"),
            ("HR", "Human Resources", "Admin", "ADM"),
            ("FIN", "Finance & Accounts", "Admin", "ADM"),
            ("IT", "Information Technology", "Service", "SRV"),
        ]
        dept_map = {}
        for code, name, dtype, parent_code in depts_data:
            parent = dept_map.get(parent_code) if parent_code else None
            d = Department(dept_code=code, dept_name=name, dept_type=dtype, parent_dept_id=parent.dept_id if parent else None)
            session.add(d)
            await session.flush()
            dept_map[code] = d
        print("Seeded Departments")

        # Production Units
        units_data = [
            ("BF-1", "Blast Furnace 1 (Godavari)", "BF", "Furnace", 3200000),
            ("BF-2", "Blast Furnace 2 (Krishna)", "BF", "Furnace", 3200000),
            ("BF-3", "Blast Furnace 3 (Kovvada)", "BF", "Furnace", 3200000),
            ("LD-1", "LD Converter 1", "SMS", "Converter", None),
            ("LD-2", "LD Converter 2", "SMS", "Converter", None),
            ("LD-3", "LD Converter 3", "SMS", "Converter", None),
            ("CCM-1", "Continuous Casting Machine 1", "CCD", "Caster", None),
            ("CCM-2", "Continuous Casting Machine 2", "CCD", "Caster", None),
            ("LMMM-1", "Light & Medium Merchant Mill", "LMMM", "Mill", None),
            ("MMSM-1", "Medium Merchant & Structural Mill", "MMSM", "Mill", None),
            ("WRM-1", "Wire Rod Mill", "WRM", "Mill", None),
        ]
        for code, name, dept_code, utype, cap in units_data:
            session.add(ProductionUnit(unit_code=code, unit_name=name, dept_id=dept_map[dept_code].dept_id, unit_type=utype, capacity_tpa=cap))
        await session.flush()
        print("Seeded Production Units")

        # Designations
        desig_titles = [
            ("Chief Executive Officer", "E10", "MGMT"),
            ("Director - Operations", "E9", "MGMT"),
            ("General Manager", "E8", None),
            ("Deputy General Manager", "E7", None),
            ("Senior Manager", "E6", None),
            ("Manager", "E5", None),
            ("Deputy Manager", "E4", None),
            ("Junior Manager", "E3", None),
            ("Technician Grade I", "S3", None),
            ("Technician Grade II", "S2", None),
            ("Technician Grade III", "S1", None),
            ("Operator", "W2", None),
            ("Helper", "W1", None),
        ]
        for title, grade, dept_code in desig_titles:
            session.add(Designation(title=title, grade=grade, dept_id=dept_map[dept_code].dept_id if dept_code else None))
        await session.flush()
        print("Seeded Designations")

        # Shifts
        shifts_data = [
            ("A", "Shift A", "06:00", "14:00", "Morning Shift"),
            ("B", "Shift B", "14:00", "22:00", "Afternoon Shift"),
            ("C", "Shift C", "22:00", "06:00", "Night Shift"),
            ("G", "General", "08:30", "17:30", "General / Office Hours"),
        ]
        shift_map = {}
        for code, name, start_str, end_str, desc in shifts_data:
            st = dt_time(*[int(x) for x in start_str.split(":")])
            et = dt_time(*[int(x) for x in end_str.split(":")])
            s = ShiftMaster(shift_code=code, shift_name=name, start_time=st, end_time=et, description=desc)
            session.add(s)
            await session.flush()
            shift_map[code] = s

        # Get designations
        result = await session.execute(
            text("SELECT title, designation_id FROM designations")
        )
        desig_map = {row[0]: row[1] for row in result.fetchall()}

        # Employees
        employees_data = [
            ("RINL0001", "A. Sharma", "MGMT", "Chief Executive Officer", "G", "ceo@vizagsteel.com"),
            ("RINL0002", "B. Verma", "BF", "Senior Manager", "G", "b.verma@vizagsteel.com"),
            ("RINL0003", "C. Reddy", "SMS", "Manager", "G", "c.reddy@vizagsteel.com"),
            ("RINL0004", "D. Patel", "QATD", "Deputy Manager", "G", "d.patel@vizagsteel.com"),
            ("RINL0005", "E. Kumar", "COCCP", "Technician Grade I", "A", "e.kumar@vizagsteel.com"),
            ("RINL0006", "F. Singh", "BF", "Operator", "B", "f.singh@vizagsteel.com"),
            ("RINL0007", "G. Rao", "SMS", "Technician Grade II", "C", "g.rao@vizagsteel.com"),
            ("RINL0008", "H. Nair", "LMMM", "Junior Manager", "G", "h.nair@vizagsteel.com"),
            ("RINL0009", "I. Joshi", "HR", "Manager", "G", "i.joshi@vizagsteel.com"),
            ("RINL0010", "J. Das", "FIN", "Deputy Manager", "G", "j.das@vizagsteel.com"),
        ]
        for emp_num, name, dept_code, desig, shift_code, email in employees_data:
            session.add(Employee(
                emp_number=emp_num, full_name=name,
                dept_id=dept_map[dept_code].dept_id,
                designation_id=desig_map.get(desig),
                shift_id=shift_map[shift_code].shift_id,
                email=email,
            ))
        await session.flush()
        print("Seeded Employees")

        # Cost Centers
        cc_data = [
            ("CC-BF", "Blast Furnace Operations", "BF"),
            ("CC-SMS", "Steel Melting Shop", "SMS"),
            ("CC-RMHP", "Raw Material Handling", "RMHP"),
            ("CC-QATD", "Quality Assurance", "QATD"),
            ("CC-HR", "Human Resources", "HR"),
        ]
        for code, name, dept_code in cc_data:
            session.add(CostCenter(cc_code=code, cc_name=name, dept_id=dept_map[dept_code].dept_id))
        await session.flush()
        print("Seeded Cost Centers")

        # Products
        products_data = [
            ("BLM-150", "Bloom 150mm x 150mm", "Semis", "Bloom", None, "150x150", "MT", None),
            ("BLT-100", "Billet 100mm x 100mm", "Semis", "Billet", None, "100x100", "MT", None),
            ("BLT-130", "Billet 130mm x 130mm", "Semis", "Billet", None, "130x130", "MT", None),
            ("TMT-12", "TMT Bar 12mm", "Long", "TMT", "Fe500D", "12mm", "MT", "IS 1786"),
            ("TMT-16", "TMT Bar 16mm", "Long", "TMT", "Fe500D", "16mm", "MT", "IS 1786"),
            ("TMT-20", "TMT Bar 20mm", "Long", "TMT", "Fe500D", "20mm", "MT", "IS 1786"),
            ("TMT-25", "TMT Bar 25mm", "Long", "TMT", "Fe500D", "25mm", "MT", "IS 1786"),
            ("TMT-32", "TMT Bar 32mm", "Long", "TMT", "Fe500D", "32mm", "MT", "IS 1786"),
            ("WR-5.5", "Wire Rod 5.5mm", "Long", "WireRod", "SAE1006", "5.5mm", "MT", None),
            ("WR-8", "Wire Rod 8mm", "Long", "WireRod", "SAE1008", "8mm", "MT", None),
            ("ANG-50", "Angle 50x50x6", "Long", "Angle", "IS2062 GrA", "50x50x6", "MT", "IS 2062"),
            ("CHN-100", "Channel 100x50", "Long", "Channel", "IS2062 GrA", "100x50", "MT", "IS 2062"),
        ]
        uom_map = {}
        result = await session.execute(text("SELECT uom_code, uom_id FROM uom_master"))
        for row in result.fetchall():
            uom_map[row[0]] = row[1]
        for code, name, cat, group, grade, size, uom, std in products_data:
            session.add(ProductCatalog(
                product_code=code, product_name=name, product_category=cat,
                product_group=group, grade=grade, size_spec=size,
                uom_id=uom_map.get(uom), standard=std,
            ))
        await session.flush()
        print("Seeded Products")

        # Materials
        materials_data = [
            ("IO-LUMP", "Iron Ore Lumps", "Raw", "IronOre", "MT", 50000),
            ("IO-FINES", "Iron Ore Fines", "Raw", "IronOre", "MT", 50000),
            ("COKING", "Coking Coal", "Raw", "Coal", "MT", 30000),
            ("NCOKING", "Non-Coking Coal", "Raw", "Coal", "MT", 10000),
            ("LIME", "Limestone", "Raw", "Flux", "MT", 10000),
            ("DOLO", "Dolomite", "Raw", "Flux", "MT", 10000),
            ("COKE-BF", "Coke (BF Grade)", "Fuel", "Coke", "MT", 5000),
            ("FESI-75", "Ferro Silicon 75%", "Raw", "FerroAlloy", "MT", 500),
            ("FEMN-70", "Ferro Manganese 70%", "Raw", "FerroAlloy", "MT", 500),
            ("ELECTRODE", "Graphite Electrode", "Consumable", "Electrode", "NOS", 50),
            ("REFR-BF", "Blast Furnace Refractory", "Refractory", "Brick", "NOS", 200),
            ("OXYGEN", "Industrial Oxygen", "Chemical", "Gas", "SCM", 100000),
        ]
        for code, name, mtype, group, uom, reorder in materials_data:
            session.add(MaterialMaster(
                material_code=code, material_name=name, material_type=mtype,
                material_group=group, uom_id=uom_map.get(uom), reorder_level=reorder,
            ))
        await session.flush()
        print("Seeded Materials")

        # ---- Seed production records (past 6 months) ----
        prod_result = await session.execute(text("SELECT product_id, product_category FROM product_catalog"))
        products = prod_result.fetchall()
        unit_result = await session.execute(text("SELECT unit_id FROM production_units"))
        units = [row[0] for row in unit_result.fetchall()]

        random.seed(42)
        today = dt_date.today()
        records = []
        for days_ago in range(180, 0, -1):
            d = today - timedelta(days=days_ago)
            if d.weekday() >= 6:
                continue
            for prod_id, category in products:
                unit_id = random.choice(units)
                base_qty = {
                    "Semis": random.uniform(800, 1200),
                    "Long": random.uniform(500, 900),
                    "Flat": random.uniform(400, 700),
                    "ByProduct": random.uniform(100, 300),
                    "Service": random.uniform(50, 150),
                }
                qty = round(base_qty.get(category, 500), 2)
                target = round(qty * random.uniform(0.9, 1.15), 2)
                yield_pct = round(random.uniform(92, 99.5), 1)
                records.append(ProductionRecord(
                    record_date=d, product_id=prod_id, unit_id=unit_id,
                    quantity=qty, target_quantity=target, yield_percent=yield_pct,
                ))
        session.add_all(records)
        await session.flush()
        print(f"Seeded {len(records)} production records")

        # ---- Seed material consumption (past 6 months) ----
        mat_result = await session.execute(text("SELECT material_id FROM material_master"))
        material_ids = [row[0] for row in mat_result.fetchall()]

        consumptions = []
        for days_ago in range(180, 0, -7):
            d = today - timedelta(days=days_ago)
            for mat_id in material_ids:
                unit_id = random.choice(units)
                qty = round(random.uniform(100, 5000), 2)
                consumptions.append(MaterialConsumption(
                    record_date=d, material_id=mat_id, unit_id=unit_id, quantity=qty,
                ))
        session.add_all(consumptions)
        await session.flush()
        print(f"Seeded {len(consumptions)} material consumption records")

        # Users with proper bcrypt hashes
        password_hash = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt(12)).decode()
        emp_result = await session.execute(
            text("SELECT emp_id, full_name FROM employees WHERE emp_number IN ('RINL0001','RINL0002','RINL0004','RINL0010')")
        )
        roles = {"RINL0001": "admin", "RINL0002": "production", "RINL0004": "qa", "RINL0010": "report_viewer"}
        for emp_id, full_name in emp_result.fetchall():
            username = full_name.split(".")[0].strip().lower()
            # find emp_number for this emp_id
            emp_num_result = await session.execute(
                text("SELECT emp_number FROM employees WHERE emp_id = :eid"), {"eid": emp_id}
            )
            emp_number = emp_num_result.scalar()
            session.add(User(
                emp_id=emp_id,
                username=username,
                password_hash=password_hash,
                role=roles.get(emp_number, "report_viewer"),
            ))
        await session.commit()
        print("Seeded Users (password for all: admin123)")

    await engine.dispose()
    print("\n=== Setup complete! ===")
    print("Login with username 'a' and password 'admin123'")


if __name__ == "__main__":
    asyncio.run(setup())
