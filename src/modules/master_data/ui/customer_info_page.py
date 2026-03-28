from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QMessageBox, QLabel, QComboBox, QHBoxLayout
)

from src.modules.master_data.services.customer_archive_service import CustomerArchiveService


class CustomerInfoPage(QWidget):
    profile_saved = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_customer_id = None
        self.create_ui()
        self.load_customer_options()
        self.load_initial_customer()

    def create_ui(self):
        main_layout = QVBoxLayout()

        title = QLabel("客户资料")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        selector_layout = QHBoxLayout()

        self.customer_selector = QComboBox()
        self.new_btn = QPushButton("新建客户")
        self.save_btn = QPushButton("保存客户")
        self.delete_btn = QPushButton("删除客户")
        self.set_default_btn = QPushButton("设为默认")
        self.reload_btn = QPushButton("刷新")

        selector_layout.addWidget(QLabel("客户档案"))
        selector_layout.addWidget(self.customer_selector, 1)
        selector_layout.addWidget(self.new_btn)
        selector_layout.addWidget(self.save_btn)
        selector_layout.addWidget(self.delete_btn)
        selector_layout.addWidget(self.set_default_btn)
        selector_layout.addWidget(self.reload_btn)

        main_layout.addLayout(selector_layout)

        form_layout = QFormLayout()

        self.customer_name_input = QLineEdit()
        self.customer_phone_input = QLineEdit()
        self.customer_address_input = QLineEdit()
        self.customer_contact_input = QLineEdit()
        self.remark_input = QLineEdit()

        form_layout.addRow("客户名称", self.customer_name_input)
        form_layout.addRow("联系电话", self.customer_phone_input)
        form_layout.addRow("客户地址", self.customer_address_input)
        form_layout.addRow("联系人", self.customer_contact_input)
        form_layout.addRow("备注", self.remark_input)

        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        self.customer_selector.currentIndexChanged.connect(self.on_customer_changed)
        self.new_btn.clicked.connect(self.new_customer)
        self.save_btn.clicked.connect(self.save_customer_info)
        self.delete_btn.clicked.connect(self.delete_customer)
        self.set_default_btn.clicked.connect(self.set_as_default_customer)
        self.reload_btn.clicked.connect(self.reload_customers)

        self.setLayout(main_layout)

    def collect_form_data(self):
        return {
            "customer_name": self.customer_name_input.text().strip(),
            "customer_phone": self.customer_phone_input.text().strip(),
            "customer_address": self.customer_address_input.text().strip(),
            "customer_contact": self.customer_contact_input.text().strip(),
            "remark": self.remark_input.text().strip(),
        }

    def set_form_data(self, data: dict):
        self.customer_name_input.setText(data.get("customer_name", ""))
        self.customer_phone_input.setText(data.get("customer_phone", ""))
        self.customer_address_input.setText(data.get("customer_address", ""))
        self.customer_contact_input.setText(data.get("customer_contact", ""))
        self.remark_input.setText(data.get("remark", ""))

    def load_customer_options(self):
        self.customer_selector.blockSignals(True)
        self.customer_selector.clear()

        options = CustomerArchiveService.get_archive_options()
        for text, value in options:
            self.customer_selector.addItem(text, value)

        self.customer_selector.blockSignals(False)

    def load_initial_customer(self):
        archive = CustomerArchiveService.get_last_used_archive()
        if archive is not None:
            self.load_archive_to_form(archive)
            self.select_customer_in_combo(archive.id)
            return

        options = CustomerArchiveService.get_archive_options()
        if options:
            first_id = options[0][1]
            archive = CustomerArchiveService.get_archive(first_id)
            if archive is not None:
                self.load_archive_to_form(archive)
                self.select_customer_in_combo(first_id)
                return

        self.new_customer()

    def select_customer_in_combo(self, customer_id: int | None):
        if customer_id is None:
            self.customer_selector.setCurrentIndex(-1)
            return

        for i in range(self.customer_selector.count()):
            if self.customer_selector.itemData(i) == customer_id:
                self.customer_selector.setCurrentIndex(i)
                return

    def load_archive_to_form(self, archive):
        self.current_customer_id = archive.id
        self.set_form_data(CustomerArchiveService.build_profile_dict(archive))

    def on_customer_changed(self):
        customer_id = self.customer_selector.currentData()
        if customer_id is None:
            return

        archive = CustomerArchiveService.get_archive(customer_id)
        if archive is None:
            return

        self.load_archive_to_form(archive)

    def new_customer(self):
        self.current_customer_id = None
        self.set_form_data({
            "customer_name": "",
            "customer_phone": "",
            "customer_address": "",
            "customer_contact": "",
            "remark": "",
        })
        self.customer_name_input.setFocus()

    def reload_customers(self):
        current_id = self.current_customer_id
        self.load_customer_options()

        if current_id is not None:
            self.select_customer_in_combo(current_id)
            archive = CustomerArchiveService.get_archive(current_id)
            if archive is not None:
                self.load_archive_to_form(archive)
                return

        self.load_initial_customer()

    def save_customer_info(self):
        try:
            success, message, customer_id = CustomerArchiveService.save_archive(
                self.collect_form_data(),
                self.current_customer_id
            )

            if not success:
                QMessageBox.warning(self, "提示", message)
                return

            self.current_customer_id = customer_id
            self.load_customer_options()
            self.select_customer_in_combo(customer_id)

            archive = CustomerArchiveService.get_archive(customer_id)
            profile = CustomerArchiveService.build_profile_dict(archive)

            self.set_form_data(profile)
            self.profile_saved.emit(profile)
            QMessageBox.information(self, "成功", message)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存客户档案失败：{e}")

    def delete_customer(self):
        if self.current_customer_id is None:
            QMessageBox.information(self, "提示", "当前没有可删除的客户档案")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除当前客户档案吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            CustomerArchiveService.delete_archive(self.current_customer_id)
            self.current_customer_id = None
            self.reload_customers()
            self.profile_saved.emit(self.collect_form_data())
            QMessageBox.information(self, "成功", "客户档案已删除")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除客户档案失败：{e}")

    def set_as_default_customer(self):
        if self.current_customer_id is None:
            QMessageBox.information(self, "提示", "请先选择一个客户档案")
            return

        try:
            CustomerArchiveService.set_last_used_customer_id(self.current_customer_id)
            archive = CustomerArchiveService.get_archive(self.current_customer_id)
            profile = CustomerArchiveService.build_profile_dict(archive)
            self.profile_saved.emit(profile)
            QMessageBox.information(self, "成功", "已设为默认客户")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"设置默认客户失败：{e}")
