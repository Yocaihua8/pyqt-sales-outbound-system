import sqlite3
import hashlib
import logging
from typing import Optional
from datetime import datetime

from .db_connections import DatabaseConnection
from src.core.models import User, OutboundRecord


logger = logging.getLogger(__name__)


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

