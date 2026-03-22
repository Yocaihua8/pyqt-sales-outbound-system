from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox
)
from src.services.stock_service import StockService


class StockManagerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_filters = {}
        self.current_data = []

        self.create_ui()
        self.load_data()

    def create_ui(self):
        layout = QVBoxLayout(self)

        filter_layout = QHBoxLayout()

        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("商品名称")

        self.warehouse_name_input = QLineEdit()
        self.warehouse_name_input.setPlaceholderText("仓库名称")

        self.low_stock_only_checkbox = QCheckBox("仅看低库存")

        self.query_btn = QPushButton("查询")
        self.query_btn.clicked.connect(self.load_data)

        self.reset_btn = QPushButton("重置")
        self.reset_btn.clicked.connect(self.reset_filters)

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_data)

        self.export_btn = QPushButton("导出当前结果")
        self.export_btn.clicked.connect(self.export_current_result)

        filter_layout.addWidget(self.product_name_input)
        filter_layout.addWidget(self.warehouse_name_input)
        filter_layout.addWidget(self.low_stock_only_checkbox)
        filter_layout.addWidget(self.query_btn)
        filter_layout.addWidget(self.reset_btn)
        filter_layout.addWidget(self.refresh_btn)
        filter_layout.addWidget(self.export_btn)

        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "商品名称", "仓库名称", "总入库", "总出库", "当前库存"
        ])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

    def collect_filters(self):
        return StockService.build_stock_filters(
            product_name=self.product_name_input.text(),
            warehouse_name=self.warehouse_name_input.text(),
            low_stock_only=self.low_stock_only_checkbox.isChecked(),
        )

    def reset_filters(self):
        self.product_name_input.clear()
        self.warehouse_name_input.clear()
        self.low_stock_only_checkbox.setChecked(False)
        self.load_data()

    def render_table_rows(self, table_rows):
        self.table.clearContents()
        self.table.setRowCount(len(table_rows))

        for row_index, row in enumerate(table_rows):
            for col_index, cell in enumerate(row):
                item = QTableWidgetItem(cell["text"])
                item.setTextAlignment(cell["alignment"])

                if cell["background"] is not None:
                    item.setBackground(cell["background"])

                self.table.setItem(row_index, col_index, item)

    def load_data(self):
        filters = self.collect_filters()
        data = StockService.get_stock_summary(**filters)

        self.current_filters = filters
        self.current_data = data

        table_rows = StockService.build_table_rows(data)
        self.render_table_rows(table_rows)

    def export_current_result(self):
        if not self.current_data:
            QMessageBox.information(self, "提示", "当前没有可导出的查询结果。")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出 CSV",
            "库存查询结果.csv",
            "CSV 文件 (*.csv)"
        )
        if not file_path:
            return

        try:
            exported_path = StockService.export_stock_to_csv(file_path, self.current_data)
            QMessageBox.information(self, "成功", f"CSV 已导出：{exported_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出 CSV 失败：{e}")

    def prepare_page(self):
        self.load_data()

