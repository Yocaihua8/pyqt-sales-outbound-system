from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
from src.repositories.auth_repository import AuthRepository
from src.services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)

class LoginDialog(QDialog):
    def __init__(self, user_dao):
        super().__init__()
        self.user_dao = user_dao
        self.auth_repo = AuthRepository(user_dao)
        self.setWindowTitle("用户登录")
        self.setFixedSize(300, 150)
        self.setModal(True)

        layout = QVBoxLayout()

        # 用户名
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("用户名:"))
        self.username_edit = QLineEdit()
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)

        # 密码
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("密码:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)

        # 按钮
        button_layout = QHBoxLayout()
        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.login)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        try:
            user = AuthService.login(self.auth_repo, username, password)
            if user:
                logger.info(f"User '{username}' logged in successfully.")
                self.accept()
            else:
                QMessageBox.critical(self, "错误", "用户名或密码错误")
                self.password_edit.clear()
        except ValueError as e:
            QMessageBox.warning(self, "警告", str(e))