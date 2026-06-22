"""
Create Phase 2 tables + seed data using pymysql only (no SQLAlchemy import
to avoid Cython extension deadlock on Windows + Python 3.11).
"""

import pymysql
import random
from datetime import date, timedelta

DB_CONFIG = {
    "host": "localhost", "port": 3306, "user": "root",
    "password": "1112", "database": "rinl_steel_plant", "charset": "utf8mb4",
}

today = date.today()
random.seed(123)

CREATE_TABLE_STATEMENTS = [
    # 1. Product Categories
    """CREATE TABLE IF NOT EXISTS product_categories (
        category_id   INT AUTO_INCREMENT PRIMARY KEY,
        category_name VARCHAR(50) NOT NULL UNIQUE,
        description   VARCHAR(255) NULL
    ) ENGINE=InnoDB""",

    # 2. Suppliers
    """CREATE TABLE IF NOT EXISTS suppliers (
        supplier_id    INT AUTO_INCREMENT PRIMARY KEY,
        supplier_code  VARCHAR(20)  NOT NULL UNIQUE,
        supplier_name  VARCHAR(150) NOT NULL,
        contact_person VARCHAR(100) NULL,
        email          VARCHAR(100) NULL,
        phone          VARCHAR(20)  NULL,
        address        TEXT         NULL,
        city           VARCHAR(50)  NULL,
        state          VARCHAR(50)  NULL,
        pincode        VARCHAR(10)  NULL,
        gst_no         VARCHAR(20)  NULL,
        rating         DECIMAL(2,1) NULL COMMENT '1.0 - 5.0',
        is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
        created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB""",

    # 3. Supplier-Material Mapping
    """CREATE TABLE IF NOT EXISTS supplier_materials (
        supplier_material_id INT AUTO_INCREMENT PRIMARY KEY,
        supplier_id          INT           NOT NULL,
        material_id          INT           NOT NULL,
        unit_price           DECIMAL(10,2) NULL,
        quality_rating       DECIMAL(2,1)  NULL,
        is_preferred         BOOLEAN       NOT NULL DEFAULT FALSE,
        contract_start       DATE          NULL,
        contract_end         DATE          NULL,
        created_at           TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_sm_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
        CONSTRAINT fk_sm_material FOREIGN KEY (material_id) REFERENCES material_master(material_id),
        UNIQUE KEY uk_supplier_material (supplier_id, material_id)
    ) ENGINE=InnoDB""",

    # 4. Material Receipts
    """CREATE TABLE IF NOT EXISTS material_receipts (
        receipt_id    INT AUTO_INCREMENT PRIMARY KEY,
        receipt_date  DATE           NOT NULL,
        supplier_id   INT            NOT NULL,
        material_id   INT            NOT NULL,
        quantity      DECIMAL(12,2)  NOT NULL,
        unit_price    DECIMAL(10,2)  NULL,
        invoice_no    VARCHAR(50)    NULL,
        quality_score DECIMAL(5,2)   NULL COMMENT '0-100 %',
        received_by   INT            NULL,
        notes         TEXT           NULL,
        created_at    TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_mr_supplier FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
        CONSTRAINT fk_mr_material FOREIGN KEY (material_id) REFERENCES material_master(material_id),
        CONSTRAINT fk_mr_receiver FOREIGN KEY (received_by) REFERENCES employees(emp_id)
    ) ENGINE=InnoDB""",

    # 5. Inventory Transactions
    """CREATE TABLE IF NOT EXISTS inventory_transactions (
        transaction_id   INT AUTO_INCREMENT PRIMARY KEY,
        transaction_date DATE         NOT NULL,
        material_id      INT          NOT NULL,
        transaction_type ENUM('IN','OUT','ADJUSTMENT') NOT NULL,
        quantity         DECIMAL(12,2) NOT NULL,
        reference_type   VARCHAR(50)  NULL COMMENT 'RECEIPT, CONSUMPTION, ADJUST, RETURN',
        reference_id     INT          NULL,
        remarks          TEXT         NULL,
        created_by       INT          NULL,
        created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_it_material FOREIGN KEY (material_id) REFERENCES material_master(material_id),
        CONSTRAINT fk_it_creator  FOREIGN KEY (created_by)  REFERENCES employees(emp_id)
    ) ENGINE=InnoDB""",

    # 6. Customers
    """CREATE TABLE IF NOT EXISTS customers (
        customer_id    INT AUTO_INCREMENT PRIMARY KEY,
        customer_code  VARCHAR(20)  NOT NULL UNIQUE,
        customer_name  VARCHAR(150) NOT NULL,
        contact_person VARCHAR(100) NULL,
        email          VARCHAR(100) NULL,
        phone          VARCHAR(20)  NULL,
        address        TEXT         NULL,
        city           VARCHAR(50)  NULL,
        state          VARCHAR(50)  NULL,
        pincode        VARCHAR(10)  NULL,
        gst_no         VARCHAR(20)  NULL,
        credit_limit   DECIMAL(12,2) NULL,
        is_active      BOOLEAN      NOT NULL DEFAULT TRUE,
        created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB""",

    # 7. Finished Products
    """CREATE TABLE IF NOT EXISTS finished_products (
        product_id    INT AUTO_INCREMENT PRIMARY KEY,
        product_code  VARCHAR(30)  NOT NULL UNIQUE,
        product_name  VARCHAR(100) NOT NULL,
        category_id   INT          NOT NULL,
        grade         VARCHAR(50)  NULL,
        size_spec     VARCHAR(50)  NULL,
        standard      VARCHAR(50)  NULL,
        uom_id        INT          NULL,
        selling_price DECIMAL(10,2) NULL,
        stock_qty     DECIMAL(12,2) NOT NULL DEFAULT 0,
        is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
        created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        CONSTRAINT fk_fp_category FOREIGN KEY (category_id) REFERENCES product_categories(category_id),
        CONSTRAINT fk_fp_uom      FOREIGN KEY (uom_id)      REFERENCES uom_master(uom_id)
    ) ENGINE=InnoDB""",

    # 8. Dispatch Header
    """CREATE TABLE IF NOT EXISTS dispatch (
        dispatch_id    INT AUTO_INCREMENT PRIMARY KEY,
        dispatch_date  DATE         NOT NULL,
        customer_id    INT          NOT NULL,
        invoice_no     VARCHAR(50)  NOT NULL UNIQUE,
        dispatch_mode  ENUM('Road','Rail','Sea') NOT NULL DEFAULT 'Road',
        vehicle_no     VARCHAR(30)  NULL,
        driver_name    VARCHAR(100) NULL,
        total_amount   DECIMAL(14,2) NULL,
        delivery_status ENUM('Planned','Dispatched','Delivered') NOT NULL DEFAULT 'Planned',
        created_by     INT          NULL,
        notes          TEXT         NULL,
        created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        CONSTRAINT fk_disp_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        CONSTRAINT fk_disp_creator  FOREIGN KEY (created_by)  REFERENCES employees(emp_id)
    ) ENGINE=InnoDB""",

    # 9. Dispatch Line Items
    """CREATE TABLE IF NOT EXISTS dispatch_items (
        dispatch_item_id INT AUTO_INCREMENT PRIMARY KEY,
        dispatch_id      INT           NOT NULL,
        product_id       INT           NOT NULL,
        quantity         DECIMAL(12,2) NOT NULL,
        unit_price       DECIMAL(10,2) NOT NULL,
        total_price      DECIMAL(14,2) GENERATED ALWAYS AS (quantity * unit_price) STORED,
        CONSTRAINT fk_di_dispatch FOREIGN KEY (dispatch_id) REFERENCES dispatch(dispatch_id) ON DELETE CASCADE,
        CONSTRAINT fk_di_product  FOREIGN KEY (product_id)  REFERENCES finished_products(product_id)
    ) ENGINE=InnoDB""",
]


def create_tables():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    for stmt in CREATE_TABLE_STATEMENTS:
        stmt = stmt.strip()
        if not stmt:
            continue
        try:
            cursor.execute(stmt)
        except pymysql.err.OperationalError as e:
            print(f"  Note (non-fatal): {e}")
    conn.commit()
    cursor.close()
    conn.close()
    print("Phase 2 tables created/verified.")


def seed_data():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Check if ALL Phase 2 data already exists; if partial, clean and re-seed
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] > 0:
        print("Data already fully seeded. Skipping.")
        cursor.close()
        conn.close()
        return
    # Clean partial data if any
    cursor.execute("DELETE FROM dispatch_items")
    cursor.execute("DELETE FROM dispatch")
    cursor.execute("DELETE FROM inventory_transactions")
    cursor.execute("DELETE FROM material_receipts")
    cursor.execute("DELETE FROM supplier_materials")
    cursor.execute("DELETE FROM finished_products")
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM suppliers")
    conn.commit()

    cursor.execute("SELECT material_id FROM material_master")
    material_ids = [r[0] for r in cursor.fetchall()]
    cursor.execute("SELECT emp_id FROM employees")
    emp_ids = [r[0] for r in cursor.fetchall()]

    # Seed categories if empty
    cursor.execute("SELECT COUNT(*) FROM product_categories")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT IGNORE INTO product_categories (category_name, description) VALUES (%s, %s)",
            [("Semis", "Blooms, Billets"), ("Long", "TMT Bars, Wire Rods, Angles, Channels"),
             ("Flat", "Plates, Sheets, Coils"), ("ByProduct", "Slag, Granulated Slag"),
             ("Service", "Services & Utilities")])
        print("Seeded product categories")

    cursor.execute("SELECT category_id, category_name FROM product_categories")
    cat_map = {name: cid for cid, name in cursor.fetchall()}

    # Seed finished_products from product_catalog if empty
    cursor.execute("SELECT COUNT(*) FROM finished_products")
    if cursor.fetchone()[0] == 0:
        for cat_name, cat_id in cat_map.items():
            selling_price = {"Long": 52000, "Semis": 38000, "Flat": 48000, "ByProduct": 1500}.get(cat_name, 10000)
            cursor.execute(
                "INSERT INTO finished_products (product_code, product_name, category_id, grade, size_spec, uom_id, selling_price, stock_qty, is_active, created_at, updated_at) "
                "SELECT product_code, product_name, %s, grade, size_spec, uom_id, %s, FLOOR(RAND() * 5000), TRUE, NOW(), NOW() "
                "FROM product_catalog WHERE product_category = %s",
                (cat_id, selling_price, cat_name))
        conn.commit()
        print("Migrated product_catalog to finished_products")

    cursor.execute("SELECT product_id FROM finished_products")
    product_ids = [r[0] for r in cursor.fetchall()]

    # 1. Suppliers (10)
    suppliers = [
        ("SUP001", "MSP Mining Corp", "Rajesh Kumar", "Mumbai", "MH", 4.5),
        ("SUP002", "Vizag Minerals Ltd", "S. Rao", "Visakhapatnam", "AP", 4.2),
        ("SUP003", "Tata Steel Mining", "A. Singh", "Jamshedpur", "JH", 4.8),
        ("SUP004", "JSW Raw Materials", "P. Patil", "Bellary", "KA", 4.0),
        ("SUP005", "SAIL Refractories", "D. Mishra", "Ranchi", "JH", 3.8),
        ("SUP006", "Indian Oxygen Co", "N. Kapoor", "Kolkata", "WB", 4.1),
        ("SUP007", "Bharat Coking Coal", "M. Mondal", "Dhanbad", "JH", 3.5),
        ("SUP008", "NMDC Iron Ore", "V. Reddy", "Hyderabad", "TG", 4.6),
        ("SUP009", "ESSAR Ferro Alloys", "K. Shah", "Ahmedabad", "GJ", 3.9),
        ("SUP010", "Adhunik Metalliks", "S. Bose", "Kolkata", "WB", 4.3),
    ]
    for code, name, contact, city, state, rating in suppliers:
            cursor.execute(
                "INSERT INTO suppliers (supplier_code, supplier_name, contact_person, email, phone, city, state, gst_no, rating, is_active, created_at, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, NOW(), NOW())",
            (code, name, contact, f"info@{name.lower().replace(' ','')}.com",
             f"98{random.randint(10000000,99999999)}", city, state,
             f"37AAAAA{random.randint(1000,9999)}A1Z5", rating))
    conn.commit()
    print("Seeded 10 suppliers")

    cursor.execute("SELECT supplier_id FROM suppliers")
    supplier_ids = [r[0] for r in cursor.fetchall()]

    # 2. Supplier-Material mappings
    for sid in supplier_ids:
        for _ in range(random.randint(2, 3)):
            mid = random.choice(material_ids)
            price = round(random.uniform(500, 25000), 2)
            try:
                cursor.execute(
                    "INSERT INTO supplier_materials (supplier_id, material_id, unit_price, quality_rating, is_preferred, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, NOW())",
                    (sid, mid, price, round(random.uniform(3.0, 5.0), 1), random.choice([True, False])))
            except pymysql.err.IntegrityError:
                pass
    conn.commit()
    print("Seeded supplier-material mappings")

    # 3. Material Receipts (20)
    for _ in range(20):
        days_ago = random.randint(1, 90)
        cursor.execute(
                "INSERT INTO material_receipts (receipt_date, supplier_id, material_id, quantity, unit_price, invoice_no, quality_score, received_by, notes, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())",
            (today - timedelta(days=days_ago), random.choice(supplier_ids), random.choice(material_ids),
             round(random.uniform(100, 5000), 2), round(random.uniform(500, 20000), 2),
             f"INV-{random.randint(10000,99999)}", round(random.uniform(85, 100), 1),
             random.choice(emp_ids), random.choice([None, None, "Rush order", "Quality checked", "Short quantity"])))
    conn.commit()
    print("Seeded 20 material receipts")

    # 4. Inventory Transactions (30)
    for _ in range(30):
        days_ago = random.randint(1, 90)
        ttype = random.choice(["IN", "OUT", "ADJUSTMENT"])
        cursor.execute(
                "INSERT INTO inventory_transactions (transaction_date, material_id, transaction_type, quantity, reference_type, reference_id, remarks, created_by, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())",
            (today - timedelta(days=days_ago), random.choice(material_ids), ttype,
             round(random.uniform(50, 3000), 2),
             random.choice(["RECEIPT", "CONSUMPTION", "ADJUST", None]),
             random.randint(1, 20) if random.random() > 0.3 else None,
             random.choice([None, None, "Monthly stocktake", "Production use"]),
             random.choice(emp_ids)))
    conn.commit()
    print("Seeded 30 inventory transactions")

    # 5. Customers (10)
    customers = [
        ("CUST001", "Reliance Steel Traders", "A. Mehta", "Mumbai", "MH", 5000000),
        ("CUST002", "Gujarat Builders Ltd", "P. Desai", "Ahmedabad", "GJ", 3000000),
        ("CUST003", "Hyderabad Infra Corp", "S. Reddy", "Hyderabad", "TG", 4000000),
        ("CUST004", "Kolkata Steel Distributors", "R. Banerjee", "Kolkata", "WB", 2500000),
        ("CUST005", "Chennai Construction Co", "K. Rajan", "Chennai", "TN", 3500000),
        ("CUST006", "Delhi Iron Traders", "V. Gupta", "Delhi", "DL", 4500000),
        ("CUST007", "Pune Auto Components", "S. Joshi", "Pune", "MH", 2000000),
        ("CUST008", "Bihar Structural Works", "A. Kumar", "Patna", "BR", 1500000),
        ("CUST009", "Karnataka Steel Syndicate", "M. Shetty", "Bengaluru", "KA", 3000000),
        ("CUST010", "Rajasthan Cement & Steel", "D. Singh", "Jaipur", "RJ", 2200000),
    ]
    for code, name, contact, city, state, credit in customers:
        cursor.execute(
            "INSERT INTO customers (customer_code, customer_name, contact_person, email, phone, city, state, gst_no, credit_limit, is_active, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, NOW(), NOW())",
            (code, name, contact, f"info@{name.lower().replace(' ','')}.com",
             f"99{random.randint(10000000,99999999)}", city, state,
             f"36BBBBB{random.randint(1000,9999)}A1Z5", credit))
    conn.commit()
    print("Seeded 10 customers")

    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [r[0] for r in cursor.fetchall()]

    # 6. Dispatches (15 with line items)
    for i in range(15):
        days_ago = random.randint(1, 60)
        cid = random.choice(customer_ids)
        invoice = f"DSP-{today.year}-{1000+i}"
        mode = random.choice(["Road", "Rail", "Sea"])
        vehicle = None
        driver = None
        if mode == "Road":
            vehicle = f"{random.choice(['AP','MH','GJ','TS','WB'])}{random.randint(10,99)}{random.choice(['A','B','C'])}{random.randint(1000,9999)}"
            driver = random.choice(["R. Sharma", "S. Singh", "P. Reddy"])
        status = random.choice(["Dispatched", "In Transit", "Delivered"])
        cursor.execute(
            "INSERT INTO dispatch (dispatch_date, customer_id, invoice_no, dispatch_mode, vehicle_no, driver_name, delivery_status, created_by, notes, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())",
            (today - timedelta(days=days_ago), cid, invoice, mode, vehicle, driver, status,
             random.choice(emp_ids), random.choice([None, None, "Urgent delivery", "High priority"])))
        dispatch_id = cursor.lastrowid
        item_count = random.randint(1, 4)
        for _ in range(item_count):
            pid = random.choice(product_ids)
            qty = round(random.uniform(10, 500), 2)
            price = round(random.uniform(35000, 55000), 2)
            cursor.execute(
                "INSERT INTO dispatch_items (dispatch_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
                (dispatch_id, pid, qty, price))
        cursor.execute(
            "UPDATE dispatch SET total_amount = (SELECT COALESCE(SUM(quantity * unit_price), 0) FROM dispatch_items WHERE dispatch_id = %s) WHERE dispatch_id = %s",
            (dispatch_id, dispatch_id))
    conn.commit()
    print("Seeded 15 dispatches with line items")

    cursor.close()
    conn.close()
    print("\n=== Seeding complete! ===")


if __name__ == "__main__":
    create_tables()
    seed_data()
