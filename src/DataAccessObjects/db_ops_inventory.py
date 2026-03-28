from src.core.constants import LOW_STOCK_THRESHOLD
from src.core.models import Warehouse, Product, InboundRecord, OutboundStockRecord
from .db_context import db_conn, warehouse_dao, product_dao, inbound_dao, outbound_stock_dao


def add_warehouse(name: str, location: str = "", remark: str = ""):
    warehouse = Warehouse(
        name=name.strip(),
        location=location.strip(),
        remark=remark.strip()
    )
    return warehouse_dao.insert(warehouse)

def get_warehouses():
    warehouses = warehouse_dao.get_all()
    return [(w.id, w.name, w.location, w.remark) for w in warehouses]

def get_warehouse_by_name(name: str):
    return warehouse_dao.get_by_name(name)

def warehouse_exists(name: str) -> bool:
    return warehouse_dao.exists_by_name(name)

def add_product(name: str, specification: str = "", unit: str = "", unit_price: float = 0.0, remark: str = ""):
    product = Product(
        name=name.strip(),
        specification=specification.strip(),
        unit=unit.strip(),
        unit_price=float(unit_price) if unit_price not in ("", None) else 0.0,
        remark=remark.strip()
    )
    return product_dao.insert(product)

def get_products():
    products = product_dao.get_all()
    return [(p.id, p.name, p.specification, p.unit, p.unit_price, p.remark) for p in products]

def get_product_by_name(name: str):
    return product_dao.get_by_name(name)

def product_exists(name: str) -> bool:
    return product_dao.exists_by_name(name)

def add_inbound_record(product_id: int, warehouse_id: int,
                       quantity: float, unit_price: float = 0.0,
                       remark: str = "", created_at=None):
    quantity = float(quantity)
    unit_price = float(unit_price)
    total_amount = quantity * unit_price

    record = InboundRecord(
        product_id=product_id,
        warehouse_id=warehouse_id,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        remark=remark.strip(),
        created_at=created_at
    )
    return inbound_dao.insert(record)

def get_inbound_records():
    return inbound_dao.get_all()

def get_stock_summary(
    product_name: str = "",
    warehouse_name: str = "",
    low_stock_only: bool = False,
    low_stock_threshold: int = LOW_STOCK_THRESHOLD
):
    cursor = db_conn.get_cursor()

    sql = """
        SELECT
            p.name,
            w.name,
            COALESCE(SUM(i.quantity), 0) AS total_in,
            COALESCE(SUM(o.quantity), 0) AS total_out,
            COALESCE(SUM(i.quantity), 0) - COALESCE(SUM(o.quantity), 0) AS stock_qty
        FROM products p
        CROSS JOIN warehouses w
        LEFT JOIN inbound_records i ON i.product_id = p.id AND i.warehouse_id = w.id
        LEFT JOIN outbound_records o ON o.product_id = p.id AND o.warehouse_id = w.id
        WHERE 1=1
    """

    params = []

    if product_name.strip():
        sql += " AND p.name LIKE ?"
        params.append(f"%{product_name.strip()}%")

    if warehouse_name.strip():
        sql += " AND w.name LIKE ?"
        params.append(f"%{warehouse_name.strip()}%")

    sql += """
        GROUP BY p.id, p.name, w.id, w.name
        HAVING stock_qty != 0
    """

    if low_stock_only:
        sql += " AND stock_qty <= ?"
        params.append(low_stock_threshold)

    sql += """
        ORDER BY p.name, w.name
    """

    cursor.execute(sql, tuple(params))
    return cursor.fetchall()

def add_outbound_record(product_id: int, warehouse_id: int,
                        quantity: float, unit_price: float = 0.0,
                        remark: str = "", created_at=None):
    quantity = float(quantity)
    unit_price = float(unit_price)
    total_amount = quantity * unit_price

    record = OutboundStockRecord(
        product_id=product_id,
        warehouse_id=warehouse_id,
        quantity=quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        remark=remark.strip(),
        created_at=created_at
    )
    return outbound_stock_dao.insert(record)

def get_outbound_records():
    return outbound_stock_dao.get_all()

def get_current_stock(product_id: int, warehouse_id: int):
    cursor = db_conn.get_cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(quantity),0)
        FROM inbound_records
        WHERE product_id=? AND warehouse_id=?
    """, (product_id, warehouse_id))
    inbound = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(quantity),0)
        FROM outbound_records
        WHERE product_id=? AND warehouse_id=?
    """, (product_id, warehouse_id))
    outbound = cursor.fetchone()[0]

    return inbound - outbound

def get_dashboard_summary():
    cursor = db_conn.get_cursor()

    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM warehouses")
    warehouse_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM inbound_records")
    inbound_count = cursor.fetchone()[0]

    stock_items = get_stock_summary()
    stock_count = len(stock_items)

    stock_total_amount = 0.0
    low_stock_count = 0

    low_stock_threshold = LOW_STOCK_THRESHOLD

    for row in stock_items:
        stock_qty = row[4] if row[4] is not None else 0

        if stock_qty <= low_stock_threshold:
            low_stock_count += 1

    return {
        "product_count": product_count,
        "warehouse_count": warehouse_count,
        "inbound_count": inbound_count,
        "stock_count": stock_count,
        "stock_total_amount": round(stock_total_amount, 2),
        "low_stock_count": low_stock_count
    }

def delete_product(product_id: int):
    cursor = db_conn.get_cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db_conn.commit()

def update_product(product_id: int, name: str, specification: str = "", unit: str = "", unit_price: float = 0.0, remark: str = ""):
    cursor = db_conn.get_cursor()
    cursor.execute("""
        UPDATE products
        SET name = ?, specification = ?, unit = ?, unit_price = ?, remark = ?
        WHERE id = ?
    """, (
        name.strip(),
        specification.strip(),
        unit.strip(),
        float(unit_price) if unit_price not in ("", None) else 0.0,
        remark.strip(),
        product_id
    ))
    db_conn.commit()

def delete_warehouse(warehouse_id: int):
    cursor = db_conn.get_cursor()
    cursor.execute("DELETE FROM warehouses WHERE id = ?", (warehouse_id,))
    db_conn.commit()

def update_warehouse(warehouse_id: int, name: str, location: str = "", remark: str = ""):
    cursor = db_conn.get_cursor()
    cursor.execute("""
        UPDATE warehouses
        SET name = ?, location = ?, remark = ?
        WHERE id = ?
    """, (
        name.strip(),
        location.strip(),
        remark.strip(),
        warehouse_id
    ))
    db_conn.commit()

