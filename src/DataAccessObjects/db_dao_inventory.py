import logging

from src.core.models import Warehouse, Product, InboundRecord, OutboundStockRecord


logger = logging.getLogger(__name__)


class WarehouseDAO:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self._create_table()

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS warehouses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            location TEXT,
            remark TEXT
        )
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(create_sql)
        self.db_conn.commit()
        logger.info("Table 'warehouses' ensured.")

    def insert(self, warehouse: Warehouse):
        insert_sql = '''
        INSERT INTO warehouses (name, location, remark)
        VALUES (?, ?, ?)
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(insert_sql, (
            warehouse.name,
            warehouse.location,
            warehouse.remark
        ))
        self.db_conn.commit()
        return cursor.lastrowid

    def insert_by_data(self, name, location="", remark=""):
        warehouse = Warehouse(
            name=name,
            location=location,
            remark=remark
        )
        return self.insert(warehouse)

    def get_all(self):
        query_sql = '''
        SELECT id, name, location, remark
        FROM warehouses
        ORDER BY id ASC
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(query_sql)
        rows = cursor.fetchall()

        warehouses = []
        for row in rows:
            warehouses.append(Warehouse(
                id=row["id"] if hasattr(row, "keys") else row[0],
                name=row["name"] if hasattr(row, "keys") else row[1],
                location=row["location"] if hasattr(row, "keys") else row[2],
                remark=row["remark"] if hasattr(row, "keys") else row[3],
            ))
        return warehouses

    def get_by_name(self, name: str):
        query_sql = '''
        SELECT id, name, location, remark
        FROM warehouses
        WHERE name = ?
        LIMIT 1
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(query_sql, (name,))
        row = cursor.fetchone()

        if not row:
            return None

        return Warehouse(
            id=row["id"] if hasattr(row, "keys") else row[0],
            name=row["name"] if hasattr(row, "keys") else row[1],
            location=row["location"] if hasattr(row, "keys") else row[2],
            remark=row["remark"] if hasattr(row, "keys") else row[3],
        )

    def exists_by_name(self, name: str) -> bool:
        query_sql = "SELECT 1 FROM warehouses WHERE name = ? LIMIT 1"
        cursor = self.db_conn.get_cursor()
        cursor.execute(query_sql, (name,))
        return cursor.fetchone() is not None

class ProductDAO:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self._create_table()

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            specification TEXT,
            unit TEXT,
            unit_price REAL,
            remark TEXT
        )
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(create_sql)
        self.db_conn.commit()
        logger.info("Table 'products' ensured.")

    def insert(self, product: Product):
        insert_sql = '''
        INSERT INTO products (name, specification, unit, unit_price, remark)
        VALUES (?, ?, ?, ?, ?)
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(insert_sql, (
            product.name,
            product.specification,
            product.unit,
            product.unit_price,
            product.remark
        ))
        self.db_conn.commit()
        return cursor.lastrowid

    def get_all(self):
        query_sql = '''
        SELECT id, name, specification, unit, unit_price, remark
        FROM products
        ORDER BY id ASC
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(query_sql)
        rows = cursor.fetchall()

        products = []
        for row in rows:
            products.append(Product(
                id=row["id"] if hasattr(row, "keys") else row[0],
                name=row["name"] if hasattr(row, "keys") else row[1],
                specification=row["specification"] if hasattr(row, "keys") else row[2],
                unit=row["unit"] if hasattr(row, "keys") else row[3],
                unit_price=row["unit_price"] if hasattr(row, "keys") else row[4],
                remark=row["remark"] if hasattr(row, "keys") else row[5],
            ))
        return products

    def get_by_name(self, name: str):
        query_sql = '''
        SELECT id, name, specification, unit, unit_price, remark
        FROM products
        WHERE name = ?
        LIMIT 1
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(query_sql, (name,))
        row = cursor.fetchone()

        if not row:
            return None

        return Product(
            id=row["id"] if hasattr(row, "keys") else row[0],
            name=row["name"] if hasattr(row, "keys") else row[1],
            specification=row["specification"] if hasattr(row, "keys") else row[2],
            unit=row["unit"] if hasattr(row, "keys") else row[3],
            unit_price=row["unit_price"] if hasattr(row, "keys") else row[4],
            remark=row["remark"] if hasattr(row, "keys") else row[5],
        )

    def exists_by_name(self, name: str) -> bool:
        query_sql = "SELECT 1 FROM products WHERE name = ? LIMIT 1"
        cursor = self.db_conn.get_cursor()
        cursor.execute(query_sql, (name,))
        return cursor.fetchone() is not None

class InboundDAO:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self._create_table()

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS inbound_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit_price REAL NOT NULL DEFAULT 0,
            total_amount REAL NOT NULL DEFAULT 0,
            remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(create_sql)
        self.db_conn.commit()
        logger.info("Table 'inbound_records' ensured.")

    def insert(self, record: InboundRecord):
        insert_sql = '''
        INSERT INTO inbound_records
        (product_id, warehouse_id, quantity, unit_price, total_amount, remark, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(insert_sql, (
            record.product_id,
            record.warehouse_id,
            record.quantity,
            record.unit_price,
            record.total_amount,
            record.remark,
            record.created_at
        ))
        self.db_conn.commit()
        return cursor.lastrowid

    def get_all(self):
        query_sql = '''
        SELECT id, product_id, warehouse_id, quantity, unit_price, total_amount, remark, created_at
        FROM inbound_records
        ORDER BY id DESC
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(query_sql)
        rows = cursor.fetchall()

        records = []
        for row in rows:
            records.append(InboundRecord(
                id=row["id"] if hasattr(row, "keys") else row[0],
                product_id=row["product_id"] if hasattr(row, "keys") else row[1],
                warehouse_id=row["warehouse_id"] if hasattr(row, "keys") else row[2],
                quantity=row["quantity"] if hasattr(row, "keys") else row[3],
                unit_price=row["unit_price"] if hasattr(row, "keys") else row[4],
                total_amount=row["total_amount"] if hasattr(row, "keys") else row[5],
                remark=row["remark"] if hasattr(row, "keys") else row[6],
                created_at=row["created_at"] if hasattr(row, "keys") else row[7],
            ))
        return records

class OutboundStockDAO:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self._create_table()

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS outbound_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            warehouse_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit_price REAL NOT NULL DEFAULT 0,
            total_amount REAL NOT NULL DEFAULT 0,
            remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(create_sql)
        self.db_conn.commit()
        logger.info("Table 'outbound_records' ensured.")

    def insert(self, record: OutboundStockRecord):
        insert_sql = '''
        INSERT INTO outbound_records
        (product_id, warehouse_id, quantity, unit_price, total_amount, remark, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(insert_sql, (
            record.product_id,
            record.warehouse_id,
            record.quantity,
            record.unit_price,
            record.total_amount,
            record.remark,
            record.created_at
        ))
        self.db_conn.commit()
        return cursor.lastrowid

    def get_all(self):
        query_sql = '''
        SELECT id, product_id, warehouse_id, quantity, unit_price, total_amount, remark, created_at
        FROM outbound_records
        ORDER BY id DESC
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(query_sql)
        rows = cursor.fetchall()

        records = []
        for row in rows:
            records.append(OutboundStockRecord(
                id=row["id"] if hasattr(row, "keys") else row[0],
                product_id=row["product_id"] if hasattr(row, "keys") else row[1],
                warehouse_id=row["warehouse_id"] if hasattr(row, "keys") else row[2],
                quantity=row["quantity"] if hasattr(row, "keys") else row[3],
                unit_price=row["unit_price"] if hasattr(row, "keys") else row[4],
                total_amount=row["total_amount"] if hasattr(row, "keys") else row[5],
                remark=row["remark"] if hasattr(row, "keys") else row[6],
                created_at=row["created_at"] if hasattr(row, "keys") else row[7],
            ))
        return records

