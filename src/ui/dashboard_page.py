from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt

from src.repositories.dashboard_repository import DashboardRepository
from src.services.dashboard_service import DashboardService


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dashboard_repo = DashboardRepository()
        self.create_ui()
        self.load_data()

    def create_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("仓库管理系统概览")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 12px;")
        layout.addWidget(title)

        self.refresh_btn = QPushButton("刷新数据")
        self.refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(self.refresh_btn)

        cards_layout = QHBoxLayout()

        self.product_card = self.create_card("商品总数", "0")
        self.warehouse_card = self.create_card("仓库总数", "0")
        self.inbound_card = self.create_card("入库记录", "0")
        self.stock_card = self.create_card("库存条目", "0")
        self.stock_amount_card = self.create_card("库存总价值", "0")
        self.low_stock_card = self.create_card("低库存商品", "0")

        cards_layout.addWidget(self.product_card["frame"])
        cards_layout.addWidget(self.warehouse_card["frame"])
        cards_layout.addWidget(self.inbound_card["frame"])
        cards_layout.addWidget(self.stock_card["frame"])
        cards_layout.addWidget(self.stock_amount_card["frame"])
        cards_layout.addWidget(self.low_stock_card["frame"])

        layout.addLayout(cards_layout)
        layout.addStretch()

    def create_card(self, title_text, value_text):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #cccccc;
                border-radius: 8px;
                background: #f8f8f8;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(frame)

        title = QLabel(title_text)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; color: #555;")

        value = QLabel(value_text)
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value.setStyleSheet("font-size: 28px; font-weight: bold; color: #222;")

        layout.addWidget(title)
        layout.addWidget(value)

        return {"frame": frame, "value": value}

    def load_data(self):
        summary = self.dashboard_repo.get_dashboard_summary()
        display_data = DashboardService.build_dashboard_summary(summary)

        self.product_card["value"].setText(display_data["product_count"])
        self.warehouse_card["value"].setText(display_data["warehouse_count"])
        self.inbound_card["value"].setText(display_data["inbound_count"])
        self.stock_card["value"].setText(display_data["stock_count"])
        self.stock_amount_card["value"].setText(display_data["stock_total_amount"])
        self.low_stock_card["value"].setText(display_data["low_stock_count"])

    def prepare_page(self):
        self.load_data()

