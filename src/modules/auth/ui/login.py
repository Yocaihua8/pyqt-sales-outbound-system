from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox)
from src.modules.auth.repositories.auth_repository import AuthRepository
from src.modules.auth.services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    def __init__(self, user_dao):
        super().__init__()
        self.user_dao = user_dao
        self.auth_repo = AuthRepository(user_dao)
        self.current_user = None
        self.setWindowTitle("\u7528\u6237\u767b\u5f55")
        self.setFixedSize(300, 150)
        self.setModal(True)

        layout = QVBoxLayout()

        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("\u7528\u6237\u540d:"))
        self.username_edit = QLineEdit()
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)

        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("\u5bc6\u7801:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)

        button_layout = QHBoxLayout()
        self.login_btn = QPushButton("\u767b\u5f55")
        self.login_btn.clicked.connect(self.login)
        self.cancel_btn = QPushButton("\u53d6\u6d88")
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
                self.current_user = user
                logger.info(f"User '{username}' logged in successfully.")
                self.accept()
            else:
                QMessageBox.critical(self, "\u9519\u8bef", "\u7528\u6237\u540d\u6216\u5bc6\u7801\u9519\u8bef")
                self.password_edit.clear()
        except ValueError as e:
            QMessageBox.warning(self, "\u8b66\u544a", str(e))

