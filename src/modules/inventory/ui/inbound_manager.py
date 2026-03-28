from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QComboBox, QMessageBox, QHeaderView
)

from src.modules.inventory.repositories.inbound_repository import InboundRepository
from src.modules.inventory.services.inbound_service import InboundService
from src.modules.inventory.services.inbound_page_service import InboundPageService
from src.modules.inventory.ui.pages.base_inventory_record_manager_page import BaseInventoryRecordManagerPage


class InboundManagerPage(BaseInventoryRecordManagerPage):
    # ---------- 初始化与界面 ----------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inbound_repo = InboundRepository()

        self.create_ui()
        self.initialize_page_data()

    def create_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QHBoxLayout()

        self.product_box = QComboBox()
        self.warehouse_box = QComboBox()

        self.qty_input = QLineEdit()
        self.price_input = QLineEdit()
        self.remark_input = QLineEdit()

        form_layout.addWidget(QLabel("商品"))
        form_layout.addWidget(self.product_box)

        form_layout.addWidget(QLabel("仓库"))
        form_layout.addWidget(self.warehouse_box)

        form_layout.addWidget(QLabel("数量"))
        form_layout.addWidget(self.qty_input)

        form_layout.addWidget(QLabel("单价"))
        form_layout.addWidget(self.price_input)

        form_layout.addWidget(QLabel("备注"))
        form_layout.addWidget(self.remark_input)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("新增入库")
        self.add_btn.clicked.connect(self.save_document)

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_data)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.refresh_btn)

        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels([
            "ID", "商品", "仓库", "数量", "单价", "金额", "时间"
        ])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

    # ---------- 公共骨架依赖 ----------
    def get_page_service(self):
        return InboundPageService

    def get_domain_service(self):
        return InboundService

    def get_repository(self):
        return self.inbound_repo

    # ---------- 保存流程差异 ----------
    def get_success_message(self) -> str:
        return "入库成功"

    # ---------- 单据页协议 ----------
    def get_document_title(self) -> str:
        return "入库管理"

    def load_document(self, order=None, items=None):
        self.load_data()



