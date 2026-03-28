from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel
)
from PyQt6.QtCore import Qt

from src.modules.sales.repositories.sales_order_repository import SalesOrderRepository
from src.modules.sales.services.sales_order_list_service import SalesOrderListService


class SalesOrderListPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.order_repo = SalesOrderRepository()

        self.create_ui()
        self.load_data()

    def create_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("销售单管理")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 8px;")
        layout.addWidget(title)

        btn_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_data)

        btn_layout.addWidget(self.refresh_btn)
        layout.addLayout(btn_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "单据编号", "录单日期", "购买单位", "发货仓库", "金额合计"
        ])
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.table.cellDoubleClicked.connect(self.open_selected_order)
        layout.addWidget(self.table)

    def load_data(self):
        orders = self.order_repo.get_sales_order_list()
        rows = SalesOrderListService.build_order_table_rows(orders)

        self.table.clearContents()
        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setTextAlignment(SalesOrderListService.get_cell_alignment(col_index))
                self.table.setItem(row_index, col_index, item)

    def open_selected_order(self, row, column):
        id_item = self.table.item(row, 0)
        if not id_item:
            return

        try:
            order_id = int(id_item.text())
        except ValueError:
            return

        if self.main_window:
            self.main_window.open_sales_order_detail(order_id)