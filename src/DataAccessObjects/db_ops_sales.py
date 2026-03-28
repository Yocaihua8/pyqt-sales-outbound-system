from src.core.models import SalesOutboundOrder, SalesOutboundItem
from .db_context import db_conn, sales_outbound_order_dao, sales_outbound_item_dao


def save_sales_outbound_document(order: SalesOutboundOrder, items: list[SalesOutboundItem]):
    cursor = db_conn.get_cursor()
    try:
        order_id = sales_outbound_order_dao.insert(order)

        for item in items:
            item.order_id = order_id
            sales_outbound_item_dao.insert(item)

        db_conn.commit()
        return order_id
    except Exception:
        db_conn.rollback()
        raise

def get_sales_outbound_orders(order_no="", customer_name="", start_date="", end_date=""):
    cursor = db_conn.get_cursor()

    sql = """
        SELECT id, order_no, order_date, warehouse_name, customer_name, total_amount
        FROM sales_outbound_orders
        WHERE 1=1
    """
    params = []

    if order_no:
        sql += " AND order_no LIKE ?"
        params.append(f"%{order_no}%")

    if customer_name:
        sql += " AND customer_name LIKE ?"
        params.append(f"%{customer_name}%")

    if start_date:
        sql += " AND order_date >= ?"
        params.append(start_date)

    if end_date:
        sql += " AND order_date <= ?"
        params.append(end_date)

    sql += " ORDER BY order_date DESC, id DESC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append((
            row["id"],
            row["order_no"],
            row["order_date"],
            row["warehouse_name"],
            row["customer_name"],
            row["total_amount"],
        ))
    return result

def get_sales_outbound_order_with_items(order_id: int):
    order = sales_outbound_order_dao.get_by_id(order_id)
    items = sales_outbound_item_dao.get_by_order_id(order_id)
    return order, items

