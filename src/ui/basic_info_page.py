from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt

from src.services.basic_info_service import BasicInfoService


class BasicInfoPage(QWidget):
    def __init__(self, parent=None, page_opener=None):
        super().__init__(parent)
        self.page_opener = page_opener
        self.create_ui()
        self.bind_events()

    def create_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("基础信息")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 12px;")
        layout.addWidget(title)

        btn_layout = QHBoxLayout()
        self.entry_buttons = {}

        for entry in BasicInfoService.get_entry_definitions():
            btn = QPushButton(entry["text"])
            btn.setMinimumHeight(60)
            btn_layout.addWidget(btn)
            self.entry_buttons[entry["key"]] = btn

        layout.addLayout(btn_layout)
        layout.addStretch()

    def bind_events(self):
        for entry in BasicInfoService.get_entry_definitions():
            btn = self.entry_buttons[entry["key"]]
            entry_type = entry["type"]
            target = entry["target"]

            if entry_type == "page":
                btn.clicked.connect(
                    lambda checked=False, target=target: self.open_entry_page(target)
                )
            else:
                btn.clicked.connect(
                    lambda checked=False, target=target: self.show_todo_message(target)
                )

    def show_todo_message(self, target: str):
        QMessageBox.information(
            self,
            "提示",
            BasicInfoService.get_todo_message(target)
        )

    def open_entry_page(self, target: str):
        if self.page_opener is None:
            QMessageBox.warning(self, "提示", "未配置页面打开入口")
            return

        self.page_opener(target)