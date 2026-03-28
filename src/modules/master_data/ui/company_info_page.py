from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.modules.master_data.services.company_archive_service import CompanyArchiveService
from PyQt6.QtWidgets import QComboBox, QHBoxLayout


class CompanyInfoPage(QWidget):
    profile_saved = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_company_id = None
        self.create_ui()
        self.load_company_options()
        self.load_initial_company()

    def create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel("公司信息")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 12px;")
        main_layout.addWidget(title)

        selector_layout = QHBoxLayout()

        self.company_selector = QComboBox()
        self.new_btn = QPushButton("新建公司")
        self.save_btn = QPushButton("保存公司")
        self.delete_btn = QPushButton("删除公司")
        self.set_default_btn = QPushButton("设为默认")
        self.reload_btn = QPushButton("刷新")

        selector_layout.addWidget(QLabel("公司档案"))
        selector_layout.addWidget(self.company_selector, 1)
        selector_layout.addWidget(self.new_btn)
        selector_layout.addWidget(self.save_btn)
        selector_layout.addWidget(self.delete_btn)
        selector_layout.addWidget(self.set_default_btn)
        selector_layout.addWidget(self.reload_btn)

        self.company_selector.currentIndexChanged.connect(self.on_company_changed)
        self.new_btn.clicked.connect(self.new_company)
        self.save_btn.clicked.connect(self.save_company_info)
        self.delete_btn.clicked.connect(self.delete_company)
        self.set_default_btn.clicked.connect(self.set_as_default_company)
        self.reload_btn.clicked.connect(self.reload_companies)

        main_layout.addLayout(selector_layout)

        form_layout = QGridLayout()

        self.company_name_input = QLineEdit()
        self.company_phone_input = QLineEdit()
        self.company_address_input = QLineEdit()
        self.company_contact_input = QLineEdit()

        form_layout.addWidget(QLabel("公司名称"), 0, 0)
        form_layout.addWidget(self.company_name_input, 0, 1)

        form_layout.addWidget(QLabel("公司电话"), 1, 0)
        form_layout.addWidget(self.company_phone_input, 1, 1)

        form_layout.addWidget(QLabel("公司地址"), 2, 0)
        form_layout.addWidget(self.company_address_input, 2, 1)

        form_layout.addWidget(QLabel("联系人"), 3, 0)
        form_layout.addWidget(self.company_contact_input, 3, 1)

        main_layout.addLayout(form_layout)

        main_layout.addStretch()

    def collect_form_data(self):
        return {
            "company_name": self.company_name_input.text().strip(),
            "company_phone": self.company_phone_input.text().strip(),
            "company_address": self.company_address_input.text().strip(),
            "company_contact": self.company_contact_input.text().strip(),
        }

    def set_form_data(self, data: dict):
        self.company_name_input.setText(data.get("company_name", ""))
        self.company_phone_input.setText(data.get("company_phone", ""))
        self.company_address_input.setText(data.get("company_address", ""))
        self.company_contact_input.setText(data.get("company_contact", ""))

    def save_company_info(self):
        try:
            success, message, company_id = CompanyArchiveService.save_archive(
                self.collect_form_data(),
                self.current_company_id
            )

            if not success:
                QMessageBox.warning(self, "提示", message)
                return

            self.current_company_id = company_id
            self.load_company_options()
            self.select_company_in_combo(company_id)

            archive = CompanyArchiveService.get_archive(company_id)
            profile = CompanyArchiveService.build_profile_dict(archive)

            self.set_form_data(profile)
            self.profile_saved.emit(profile)
            QMessageBox.information(self, "成功", message)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存公司档案失败：{e}")

    def load_company_options(self):
        self.company_selector.blockSignals(True)
        self.company_selector.clear()

        options = CompanyArchiveService.get_archive_options()
        for text, value in options:
            self.company_selector.addItem(text, value)

        self.company_selector.blockSignals(False)

    def load_initial_company(self):
        CompanyArchiveService.migrate_legacy_profile_if_needed()

        archive = CompanyArchiveService.get_last_used_archive()
        if archive is not None:
            self.load_archive_to_form(archive)
            self.select_company_in_combo(archive.id)
            return

        options = CompanyArchiveService.get_archive_options()
        if options:
            first_id = options[0][1]
            archive = CompanyArchiveService.get_archive(first_id)
            if archive is not None:
                self.load_archive_to_form(archive)
                self.select_company_in_combo(first_id)
                return

        self.new_company()

    def select_company_in_combo(self, company_id: int | None):
        if company_id is None:
            self.company_selector.setCurrentIndex(-1)
            return

        for i in range(self.company_selector.count()):
            if self.company_selector.itemData(i) == company_id:
                self.company_selector.setCurrentIndex(i)
                return

    def load_archive_to_form(self, archive):
        self.current_company_id = archive.id
        self.set_form_data(CompanyArchiveService.build_profile_dict(archive))

    def on_company_changed(self):
        company_id = self.company_selector.currentData()
        if company_id is None:
            return

        archive = CompanyArchiveService.get_archive(company_id)
        if archive is None:
            return

        self.load_archive_to_form(archive)

    def new_company(self):
        self.current_company_id = None
        self.set_form_data({
            "company_name": "",
            "company_phone": "",
            "company_address": "",
            "company_contact": "",
        })
        self.company_name_input.setFocus()

    def reload_companies(self):
        current_id = self.current_company_id
        self.load_company_options()

        if current_id is not None:
            self.select_company_in_combo(current_id)
            archive = CompanyArchiveService.get_archive(current_id)
            if archive is not None:
                self.load_archive_to_form(archive)
                return

        self.load_initial_company()

    def delete_company(self):
        if self.current_company_id is None:
            QMessageBox.information(self, "提示", "当前没有可删除的公司档案")
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除当前公司档案吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            CompanyArchiveService.delete_archive(self.current_company_id)
            self.current_company_id = None
            self.reload_companies()
            self.profile_saved.emit({
                "company_name": self.company_name_input.text().strip(),
                "company_phone": self.company_phone_input.text().strip(),
                "company_address": self.company_address_input.text().strip(),
                "company_contact": self.company_contact_input.text().strip(),
            })
            QMessageBox.information(self, "成功", "公司档案已删除")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除公司档案失败：{e}")

    def set_as_default_company(self):
        if self.current_company_id is None:
            QMessageBox.information(self, "提示", "请先选择一个公司档案")
            return

        try:
            CompanyArchiveService.set_last_used_company_id(self.current_company_id)
            archive = CompanyArchiveService.get_archive(self.current_company_id)
            profile = CompanyArchiveService.build_profile_dict(archive)
            self.profile_saved.emit(profile)
            QMessageBox.information(self, "成功", "已设为默认公司")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"设置默认公司失败：{e}")
