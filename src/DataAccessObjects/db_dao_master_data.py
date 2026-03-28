import logging


logger = logging.getLogger(__name__)


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

