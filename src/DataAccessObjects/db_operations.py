import sqlite3
import hashlib
import logging
from typing import Optional
from datetime import datetime
from .db_connections import DatabaseConnection
from src.core.constants import LOW_STOCK_THRESHOLD
from src.core.models import (
    User, OutboundRecord, Warehouse, Product,
    InboundRecord, OutboundStockRecord,
    SalesOutboundOrder, SalesOutboundItem
)

logger = logging.getLogger(__name__)

# ---------- 密码哈希工具 ----------
def hash_password(password: str, salt: str = "fixed_salt") -> str:
    """简单哈希密码（实际应用中应使用更安全的方式）"""
    return hashlib.sha256((password + salt).encode()).hexdigest()


class OutboundDAO:
    def __init__(self, db_conn: DatabaseConnection):
        self.db_conn = db_conn
        self._create_table()

    def _create_table(self):
        """创建表（如果不存在）"""
        create_sql = '''
            CREATE TABLE IF NOT EXISTS outbound (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT,
                specification TEXT,
                color TEXT,
                pieces INTEGER,
                quantity REAL,
                unit_price REAL,
                amount REAL,
                remark TEXT
            )
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(create_sql)
        self.db_conn.commit()
        logger.info("Table 'outbound' ensured.")

    def get_all(self):
        """获取所有记录，返回 OutboundRecord 列表"""
        cursor = self.db_conn.get_cursor()
        cursor.execute("SELECT id, product_name, specification, color, pieces, quantity, unit_price, amount, remark FROM outbound")
        rows = cursor.fetchall()
        records = []
        for row in rows:
            # row 是 sqlite3.Row 对象，支持索引和键访问
            record = OutboundRecord(
                id=row['id'],
                product_name=row['product_name'],
                specification=row['specification'],
                color=row['color'],
                pieces=row['pieces'],
                quantity=row['quantity'],
                unit_price=row['unit_price'],
                amount=row['amount'],
                remark=row['remark']
            )
            records.append(record)
        logger.debug(f"Fetched {len(records)} records from outbound.")
        return records

    def insert(self, record: OutboundRecord):
        """插入新记录，返回新id"""
        insert_sql = '''
            INSERT INTO outbound 
            (product_name, specification, color, pieces, quantity, unit_price, amount, remark)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(insert_sql, record.to_tuple())
        self.db_conn.commit()
        new_id = cursor.lastrowid
        logger.info(f"Inserted record with id {new_id}")
        return new_id

    def update(self, record: OutboundRecord):
        """更新现有记录（必须包含id）"""
        if record.id is None:
            raise ValueError("Cannot update record without id.")
        update_sql = '''
            UPDATE outbound SET
                product_name = ?,
                specification = ?,
                color = ?,
                pieces = ?,
                quantity = ?,
                unit_price = ?,
                amount = ?,
                remark = ?
            WHERE id = ?
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(update_sql, record.to_tuple() + (record.id,))
        self.db_conn.commit()
        logger.info(f"Updated record with id {record.id}")

    def delete(self, record_id: int):
        """删除指定id的记录"""
        delete_sql = "DELETE FROM outbound WHERE id = ?"
        cursor = self.db_conn.get_cursor()
        cursor.execute(delete_sql, (record_id,))
        self.db_conn.commit()
        logger.info(f"Deleted record with id {record_id}")

class UserDAO:
    """用户数据访问对象"""
    def __init__(self, db_conn: DatabaseConnection):
        self.db_conn = db_conn
        self._create_table()
        self._ensure_admin()  # 确保至少有一个管理员

    def _create_table(self):
        """创建用户表（如果不存在）"""
        create_sql = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(create_sql)
        self.db_conn.commit()
        logger.info("Table 'users' ensured.")

    def _ensure_admin(self):
        """确保至少有一个管理员账户（默认 admin/admin）"""
        cursor = self.db_conn.get_cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        count = cursor.fetchone()[0]
        if count == 0:
            # 创建默认管理员
            default_admin = User(
                username="admin",
                password_hash=hash_password("admin"),
                role="admin",
                created_at=datetime.now()
            )
            self.insert(default_admin)
            logger.info("Created default admin account (username=admin, password=admin)")

    def insert(self, user: User) -> int:
        """插入新用户"""
        insert_sql = '''
            INSERT INTO users (username, password_hash, role, created_at)
            VALUES (?, ?, ?, ?)
        '''
        cursor = self.db_conn.get_cursor()
        try:
            cursor.execute(insert_sql, (user.username, user.password_hash, user.role, user.created_at))
            self.db_conn.commit()
            new_id = cursor.lastrowid
            logger.info(f"Inserted user '{user.username}' with id {new_id}")
            return new_id
        except sqlite3.IntegrityError as e:
            logger.error(f"Username '{user.username}' already exists.")
            raise ValueError("用户名已存在") from e

    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        cursor = self.db_conn.get_cursor()
        cursor.execute("SELECT id, username, password_hash, role, created_at FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                role=row['role'],
                created_at=row['created_at']
            )
        return None

    def get_all(self) -> list[User]:
        """获取所有用户（按id升序）"""
        cursor = self.db_conn.get_cursor()
        cursor.execute("SELECT id, username, password_hash, role, created_at FROM users ORDER BY id")
        rows = cursor.fetchall()
        users = []
        for row in rows:
            users.append(User(
                id=row['id'],
                username=row['username'],
                password_hash=row['password_hash'],
                role=row['role'],
                created_at=row['created_at']
            ))
        return users

    def update_password(self, user_id: int, new_password_hash: str):
        """更新用户密码"""
        update_sql = "UPDATE users SET password_hash = ? WHERE id = ?"
        cursor = self.db_conn.get_cursor()
        cursor.execute(update_sql, (new_password_hash, user_id))
        self.db_conn.commit()
        logger.info(f"Updated password for user id {user_id}")

    def update_role(self, user_id: int, new_role: str):
        """更新用户角色"""
        update_sql = "UPDATE users SET role = ? WHERE id = ?"
        cursor = self.db_conn.get_cursor()
        cursor.execute(update_sql, (new_role, user_id))
        self.db_conn.commit()
        logger.info(f"Updated role for user id {user_id} to {new_role}")

    def delete(self, user_id: int):
        """删除用户（禁止删除最后一个管理员）"""
        # 先检查是否最后一个管理员
        cursor = self.db_conn.get_cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        if admin_count <= 1:
            cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row and row['role'] == 'admin':
                raise ValueError("不能删除最后一个管理员账户")

        delete_sql = "DELETE FROM users WHERE id = ?"
        cursor.execute(delete_sql, (user_id,))
        self.db_conn.commit()
        logger.info(f"Deleted user id {user_id}")

    def validate_login(self, username: str, password: str) -> Optional[User]:
        """验证登录，成功返回User对象，否则返回None"""
        user = self.get_by_username(username)
        if user and user.password_hash == hash_password(password):
            return user
        return None

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

class CompanyDAO:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self._create_table()

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            company_phone TEXT DEFAULT '',
            company_address TEXT DEFAULT '',
            company_contact TEXT DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(create_sql)
        self.db_conn.commit()

    def insert(self, company_name: str, company_phone: str = "", company_address: str = "", company_contact: str = ""):
        cursor = self.db_conn.get_cursor()
        cursor.execute("""
            INSERT INTO companies (
                company_name, company_phone, company_address, company_contact
            ) VALUES (?, ?, ?, ?)
        """, (company_name, company_phone, company_address, company_contact))
        self.db_conn.commit()
        return cursor.lastrowid

    def update(self, company_id: int, company_name: str, company_phone: str = "", company_address: str = "",
               company_contact: str = ""):
        cursor = self.db_conn.get_cursor()
        cursor.execute("""
            UPDATE companies
            SET company_name = ?, company_phone = ?, company_address = ?, company_contact = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (company_name, company_phone, company_address, company_contact, company_id))
        self.db_conn.commit()

    def delete(self, company_id: int):
        cursor = self.db_conn.get_cursor()
        cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))
        self.db_conn.commit()

    def get_all(self):
        cursor = self.db_conn.get_cursor()
        cursor.execute("""
            SELECT id, company_name, company_phone, company_address, company_contact, is_active, created_at, updated_at
            FROM companies
            ORDER BY id DESC
        """)
        return cursor.fetchall()

    def get_by_id(self, company_id: int):
        cursor = self.db_conn.get_cursor()
        cursor.execute("""
            SELECT id, company_name, company_phone, company_address, company_contact, is_active, created_at, updated_at
            FROM companies
            WHERE id = ?
            LIMIT 1
        """, (company_id,))
        return cursor.fetchone()

class CustomerDAO:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self._create_table()

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_phone TEXT DEFAULT '',
            customer_address TEXT DEFAULT '',
            customer_contact TEXT DEFAULT '',
            remark TEXT DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(create_sql)
        self.db_conn.commit()

    def insert(self, customer_name: str, customer_phone: str = "", customer_address: str = "",
               customer_contact: str = "", remark: str = ""):
        cursor = self.db_conn.get_cursor()
        cursor.execute("""
            INSERT INTO customers (
                customer_name, customer_phone, customer_address, customer_contact, remark
            ) VALUES (?, ?, ?, ?, ?)
        """, (customer_name, customer_phone, customer_address, customer_contact, remark))
        self.db_conn.commit()
        return cursor.lastrowid

    def update(self, customer_id: int, customer_name: str, customer_phone: str = "", customer_address: str = "",
               customer_contact: str = "", remark: str = ""):
        cursor = self.db_conn.get_cursor()
        cursor.execute("""
            UPDATE customers
            SET customer_name = ?, customer_phone = ?, customer_address = ?, customer_contact = ?, remark = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (customer_name, customer_phone, customer_address, customer_contact, remark, customer_id))
        self.db_conn.commit()

    def delete(self, customer_id: int):
        cursor = self.db_conn.get_cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        self.db_conn.commit()

    def get_all(self):
        cursor = self.db_conn.get_cursor()
        cursor.execute("""
            SELECT id, customer_name, customer_phone, customer_address, customer_contact, remark, is_active, created_at, updated_at
            FROM customers
            ORDER BY id DESC
        """)
        return cursor.fetchall()

    def get_by_id(self, customer_id: int):
        cursor = self.db_conn.get_cursor()
        cursor.execute("""
            SELECT id, customer_name, customer_phone, customer_address, customer_contact, remark, is_active, created_at, updated_at
            FROM customers
            WHERE id = ?
            LIMIT 1
        """, (customer_id,))
        return cursor.fetchone()

class AppSettingDAO:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self._create_table()

    def _create_table(self):
        create_sql = '''
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        '''
        cursor = self.db_conn.get_cursor()
        cursor.execute(create_sql)
        self.db_conn.commit()

    def get_value(self, key: str):
        cursor = self.db_conn.get_cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        if not row:
            return None
        return row["value"] if hasattr(row, "keys") else row[0]

    def set_value(self, key: str, value: str):
        cursor = self.db_conn.get_cursor()
        cursor.execute("""
            INSERT INTO app_settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (key, value))
        self.db_conn.commit()

db_conn = DatabaseConnection()
user_dao = UserDAO(db_conn)
outbound_dao = OutboundDAO(db_conn)
warehouse_dao = WarehouseDAO(db_conn)
product_dao = ProductDAO(db_conn)
inbound_dao = InboundDAO(db_conn)
outbound_stock_dao = OutboundStockDAO(db_conn)
sales_outbound_order_dao = SalesOutboundOrderDAO(db_conn)
sales_outbound_item_dao = SalesOutboundItemDAO(db_conn)
company_dao = CompanyDAO(db_conn)
customer_dao = CustomerDAO(db_conn)
app_setting_dao = AppSettingDAO(db_conn)

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

def get_warehouse_id_by_name(name: str):
    warehouse = warehouse_dao.get_by_name(name)
    return warehouse.id if warehouse else None

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

def get_product_id_by_name(name: str):
    product = product_dao.get_by_name(name)
    return product.id if product else None

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

def add_sales_outbound_order(order: SalesOutboundOrder):
    return sales_outbound_order_dao.insert(order)

def add_sales_outbound_item(item: SalesOutboundItem):
    return sales_outbound_item_dao.insert(item)

def get_sales_outbound_order(order_id: int):
    return sales_outbound_order_dao.get_by_id(order_id)

def get_sales_outbound_items(order_id: int):
    return sales_outbound_item_dao.get_by_order_id(order_id)

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

def add_company(company_name: str, company_phone: str = "", company_address: str = "", company_contact: str = ""):
    return company_dao.insert(
        company_name.strip(),
        company_phone.strip(),
        company_address.strip(),
        company_contact.strip()
    )

def update_company(company_id: int, company_name: str, company_phone: str = "", company_address: str = "", company_contact: str = ""):
    company_dao.update(
        company_id,
        company_name.strip(),
        company_phone.strip(),
        company_address.strip(),
        company_contact.strip()
    )

def delete_company(company_id: int):
    company_dao.delete(company_id)

def get_all_companies():
    return company_dao.get_all()

def get_company_by_id(company_id: int):
    return company_dao.get_by_id(company_id)

def get_app_setting(key: str):
    return app_setting_dao.get_value(key)

def set_app_setting(key: str, value: str):
    app_setting_dao.set_value(key, value)

def add_customer(customer_name: str, customer_phone: str = "", customer_address: str = "",
                 customer_contact: str = "", remark: str = ""):
    return customer_dao.insert(
        customer_name.strip(),
        customer_phone.strip(),
        customer_address.strip(),
        customer_contact.strip(),
        remark.strip()
    )

def update_customer(customer_id: int, customer_name: str, customer_phone: str = "", customer_address: str = "",
                    customer_contact: str = "", remark: str = ""):
    customer_dao.update(
        customer_id,
        customer_name.strip(),
        customer_phone.strip(),
        customer_address.strip(),
        customer_contact.strip(),
        remark.strip()
    )

def delete_customer(customer_id: int):
    customer_dao.delete(customer_id)

def get_all_customers():
    return customer_dao.get_all()

def get_customer_by_id(customer_id: int):
    return customer_dao.get_by_id(customer_id)


