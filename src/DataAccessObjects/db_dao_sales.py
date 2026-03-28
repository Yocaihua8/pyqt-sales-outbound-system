import logging

from src.core.models import SalesOutboundOrder, SalesOutboundItem


logger = logging.getLogger(__name__)


class SalesOutboundOrderDAO:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self._create_table()

    def _ensure_column(self, table_name: str, column_name: str, column_def: str):
        cursor = self.db_conn.get_cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row["name"] if hasattr(row, "keys") else row[1] for row in cursor.fetchall()]
        if column_name not in columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
            self.db_conn.commit()

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS sales_outbound_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT UNIQUE,
            order_date TEXT,
            warehouse_name TEXT,

            customer_name TEXT,
            customer_phone TEXT,
            customer_address TEXT,
            customer_contact TEXT,

            summary_remark TEXT,

            total_amount REAL DEFAULT 0,
            amount_in_words TEXT,

            company_name TEXT,
            company_phone TEXT,
            company_address TEXT,
            company_contact TEXT,

            handler TEXT,
            recorder TEXT,
            reviewer TEXT,
            sign_remark TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(create_sql)
        self.db_conn.commit()

        self._ensure_column("sales_outbound_orders", "company_id", "INTEGER")
        self._ensure_column("sales_outbound_orders", "customer_id", "INTEGER")

    def insert(self, order: SalesOutboundOrder):
        insert_sql = '''
            INSERT INTO sales_outbound_orders (
                order_no, order_date, warehouse_name,
                customer_id, customer_name, customer_phone, customer_address, customer_contact,
                summary_remark,
                total_amount, amount_in_words,
                company_id, company_name, company_phone, company_address, company_contact,
                handler, recorder, reviewer, sign_remark,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(insert_sql, (
            order.order_no,
            order.order_date,
            order.warehouse_name,

            order.customer_id,
            order.customer_name,
            order.customer_phone,
            order.customer_address,
            order.customer_contact,

            order.summary_remark,

            order.total_amount,
            order.amount_in_words,

            order.company_id,
            order.company_name,
            order.company_phone,
            order.company_address,
            order.company_contact,

            order.handler,
            order.recorder,
            order.reviewer,
            order.sign_remark,

            order.created_at
        ))
        self.db_conn.commit()
        return cursor.lastrowid

    def get_by_id(self, order_id: int):
        cursor = self.db_conn.get_cursor()
        cursor.execute("SELECT * FROM sales_outbound_orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        if not row:
            return None

        return SalesOutboundOrder(
            id=row["id"],
            order_no=row["order_no"],
            order_date=row["order_date"],
            warehouse_name=row["warehouse_name"],
            customer_name=row["customer_name"],
            customer_phone=row["customer_phone"],
            customer_address=row["customer_address"],
            customer_contact=row["customer_contact"],
            summary_remark=row["summary_remark"],
            total_amount=row["total_amount"],
            amount_in_words=row["amount_in_words"],
            company_name=row["company_name"],
            company_phone=row["company_phone"],
            company_address=row["company_address"],
            company_contact=row["company_contact"],
            handler=row["handler"],
            recorder=row["recorder"],
            reviewer=row["reviewer"],
            sign_remark=row["sign_remark"],
            created_at=row["created_at"],
            customer_id = row["customer_id"],
            company_id = row["company_id"],
        )

    def get_all(self):
        cursor = self.db_conn.get_cursor()
        cursor.execute("""
            SELECT *
            FROM sales_outbound_orders
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()

        orders = []
        for row in rows:
            orders.append(SalesOutboundOrder(
                id=row["id"],
                order_no=row["order_no"],
                order_date=row["order_date"],
                warehouse_name=row["warehouse_name"],
                customer_name=row["customer_name"],
                customer_phone=row["customer_phone"],
                customer_address=row["customer_address"],
                customer_contact=row["customer_contact"],
                summary_remark=row["summary_remark"],
                total_amount=row["total_amount"],
                amount_in_words=row["amount_in_words"],
                company_name=row["company_name"],
                company_phone=row["company_phone"],
                company_address=row["company_address"],
                company_contact=row["company_contact"],
                handler=row["handler"],
                recorder=row["recorder"],
                reviewer=row["reviewer"],
                sign_remark=row["sign_remark"],
                created_at=row["created_at"],
                customer_id=row["customer_id"],
                company_id=row["company_id"],
            ))
        return orders

class SalesOutboundItemDAO:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self._create_table()

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS sales_outbound_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            line_no INTEGER,
            product_name TEXT,
            specification TEXT,
            color TEXT,
            pieces INTEGER,
            quantity REAL,
            unit_price REAL,
            amount REAL,
            remark TEXT,
            FOREIGN KEY(order_id) REFERENCES sales_outbound_orders(id)
        )
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(create_sql)
        self.db_conn.commit()
        logger.info("Table 'sales_outbound_items' ensured.")

    def insert(self, item: SalesOutboundItem):
        insert_sql = '''
        INSERT INTO sales_outbound_items (
            order_id, line_no, product_name, specification, color,
            pieces, quantity, unit_price, amount, remark
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(insert_sql, (
            item.order_id,
            item.line_no,
            item.product_name,
            item.specification,
            item.color,
            item.pieces,
            item.quantity,
            item.unit_price,
            item.amount,
            item.remark
        ))
        self.db_conn.commit()
        return cursor.lastrowid

    def get_by_order_id(self, order_id: int):
        cursor = self.db_conn.get_cursor()
        cursor.execute("""
            SELECT * FROM sales_outbound_items
            WHERE order_id = ?
            ORDER BY line_no ASC, id ASC
        """, (order_id,))
        rows = cursor.fetchall()

        items = []
        for row in rows:
            items.append(SalesOutboundItem(
                id=row["id"],
                order_id=row["order_id"],
                line_no=row["line_no"],
                product_name=row["product_name"],
                specification=row["specification"],
                color=row["color"],
                pieces=row["pieces"],
                quantity=row["quantity"],
                unit_price=row["unit_price"],
                amount=row["amount"],
                remark=row["remark"]
            ))
        return items

    def delete_by_order_id(self, order_id: int):
        cursor = self.db_conn.get_cursor()
        cursor.execute("DELETE FROM sales_outbound_items WHERE order_id = ?", (order_id,))
        self.db_conn.commit()

