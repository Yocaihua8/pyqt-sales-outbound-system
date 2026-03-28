from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QComboBox, QMessageBox, QHeaderView
)

from src.modules.inventory.repositories.outbound_repository import OutboundRepository
from src.modules.inventory.services.outbound_service import OutboundService
from src.modules.inventory.services.outbound_page_service import OutboundPageService
from src.modules.inventory.ui.pages.base_inventory_record_manager_page import BaseInventoryRecordManagerPage


class OutboundManagerPage(BaseInventoryRecordManagerPage):
    # ---------- 初始化与界面 ----------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.outbound_repo = OutboundRepository()

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

        self.stock_label = QLabel("当前库存: -")
        form_layout.addWidget(self.stock_label)

        form_layout.addWidget(QLabel("数量"))
        form_layout.addWidget(self.qty_input)

        form_layout.addWidget(QLabel("单价"))
        form_layout.addWidget(self.price_input)

        form_layout.addWidget(QLabel("备注"))
        form_layout.addWidget(self.remark_input)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("新增出库")
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

        self.product_box.currentIndexChanged.connect(self.update_stock_display)
        self.warehouse_box.currentIndexChanged.connect(self.update_stock_display)

        layout.addWidget(self.table)

    # ---------- 公共骨架依赖 ----------
    def get_page_service(self):
        return OutboundPageService

    def get_domain_service(self):
        return OutboundService

    def get_repository(self):
        return self.outbound_repo

    def after_load_products(self):
        self.update_stock_display()

    def after_load_warehouses(self):
        self.update_stock_display()

    def after_load_data(self):
        self.update_stock_display()

    def update_stock_display(self):
        OutboundPageService.refresh_stock_label(self, self.outbound_repo, OutboundService)

    # ---------- 保存流程差异 ----------
    def get_success_message(self) -> str:
        return "出库成功"

    def before_save_record(self, form_raw: dict, form_data: dict):
        current_stock = self.outbound_repo.get_current_stock(
            form_raw["product_id"],
            form_raw["warehouse_id"]
        )
        OutboundService.validate_stock(form_data["qty"], current_stock)

    def after_save_record(self):
        self.update_stock_display()

    def after_prepare_new_document(self):
        self.update_stock_display()

    # ---------- 单据页协议 ----------
    def get_document_title(self) -> str:
        return "出库管理"

    def load_document(self, order=None, items=None):
        self.load_data()
        self.update_stock_display()


