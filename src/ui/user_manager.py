import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QHeaderView,
    QMessageBox, QInputDialog, QLineEdit, QAbstractItemView
)
from PyQt6.QtCore import Qt

from src.services.user_service import UserService
from src.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

class UserManagerDialog(QDialog):
    def __init__(self, user_dao, parent=None):
        super().__init__(parent)
        self.user_dao = user_dao
        self.user_repo = UserRepository(user_dao)
        self.setWindowTitle("用户管理")
        self.resize(600, 400)

        layout = QVBoxLayout()

        # 用户表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "用户名", "角色", "创建时间"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # 按钮栏
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加用户")
        add_btn.clicked.connect(self.add_user)
        btn_layout.addWidget(add_btn)

        edit_role_btn = QPushButton("修改角色")
        edit_role_btn.clicked.connect(self.edit_role)
        btn_layout.addWidget(edit_role_btn)

        reset_pwd_btn = QPushButton("重置密码")
        reset_pwd_btn.clicked.connect(self.reset_password)
        btn_layout.addWidget(reset_pwd_btn)

        del_btn = QPushButton("删除用户")
        del_btn.clicked.connect(self.delete_user)
        btn_layout.addWidget(del_btn)

        btn_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.load_users()

    def load_users(self):
        users = self.user_repo.get_all_users()
        rows = UserService.build_user_table_rows(users)

        self.table.clearContents()
        self.table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)

        self.table.resizeColumnsToContents()

    def add_user(self):
        """添加用户"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("添加用户")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("用户名:"))
        username_edit = QLineEdit()
        layout.addWidget(username_edit)

        layout.addWidget(QLabel("密码:"))
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(password_edit)

        layout.addWidget(QLabel("角色:"))
        role_combo = QComboBox()
        role_combo.addItems(["user", "admin"])
        layout.addWidget(role_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            username = username_edit.text().strip()
            password = password_edit.text()
            role = role_combo.currentText()

            try:
                user = UserService.build_new_user(username, password, role)
                self.user_repo.insert_user(user)
                self.load_users()
                logger.info(f"Added user {username}")
            except ValueError as e:
                QMessageBox.critical(self, "错误", str(e))

    def edit_role(self):
        """修改选中用户的角色"""
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "警告", "请先选择一个用户")
            return

        user_id = int(self.table.item(selected, 0).text())
        current_role = self.table.item(selected, 2).text()

        role, ok = QInputDialog.getItem(
            self,
            "修改角色",
            "选择新角色:",
            ["user", "admin"],
            0,
            False
        )
        if ok and role:
            try:
                changed = UserService.validate_new_role(current_role, role)
                if not changed:
                    return

                self.user_repo.update_user_role(user_id, role)
                self.load_users()
                logger.info(f"Updated user {user_id} role to {role}")
            except ValueError as e:
                QMessageBox.critical(self, "错误", str(e))
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))

    def reset_password(self):
        """重置选中用户的密码"""
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "警告", "请先选择一个用户")
            return

        user_id = int(self.table.item(selected, 0).text())
        username = self.table.item(selected, 1).text()

        new_password, ok = QInputDialog.getText(self, "重置密码",
                                                f"输入用户 '{username}' 的新密码:",
                                                QLineEdit.EchoMode.Password)
        if ok:
            try:
                password_hash = UserService.validate_new_password(new_password)
                self.user_repo.update_user_password(user_id, password_hash)
                QMessageBox.information(self, "成功", "密码已重置")
                logger.info(f"Reset password for user {username}")
            except ValueError as e:
                QMessageBox.warning(self, "警告", str(e))
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))

    def delete_user(self):
        """删除选中用户"""
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "警告", "请先选择一个用户")
            return

        user_id = int(self.table.item(selected, 0).text())
        username = self.table.item(selected, 1).text()

        try:
            current_username = self.parent().current_user.username
            UserService.validate_delete_user(username, current_username)
        except ValueError as e:
            QMessageBox.warning(self, "警告", str(e))
            return
        except Exception:
            # 如果父窗口没有 current_user，先跳过该规则，避免界面直接崩
            pass

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定删除用户 '{username}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self.user_repo.delete_user(user_id)
            self.load_users()
            logger.info(f"Deleted user {username}")
        except ValueError as e:
            QMessageBox.critical(self, "错误", str(e))
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))