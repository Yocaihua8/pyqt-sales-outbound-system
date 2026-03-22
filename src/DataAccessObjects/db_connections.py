import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self, db_name="warehouse.db"):

        # 当前文件位置 src/DataAccessObjects/
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 项目根目录 OutboundOrderSystem2.0/
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

        # database 文件夹
        db_dir = os.path.join(project_root, "database")
        os.makedirs(db_dir, exist_ok=True)

        # 最终数据库路径
        self.db_path = os.path.join(db_dir, db_name)

        print("当前数据库路径:", self.db_path)

        self.connection = None

    def connect(self):
        """建立数据库连接"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        return self.connection

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_cursor(self):
        return self.connect().cursor()

    def commit(self):
        if self.connection:
            self.connection.commit()

    def rollback(self):
        if self.connection:
            self.connection.rollback()