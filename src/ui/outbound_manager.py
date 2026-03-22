from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView
)

from src.repositories.outbound_repository import OutboundRepository
from src.services.outbound_service import OutboundService
from src.services.outbound_page_service import OutboundPageService
from src.ui.base_document_page import BaseDocumentPage

class OutboundManagerPage(BaseDocumentPage):
    # ---------- 初始化与界面 ----------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.outbound_repo = OutboundRepository()

        self.create_ui()
        self.load_products()
        self.load_warehouses()
        self.load_data()

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

    # ---------- 页面初始化数据 ----------
    def load_products(self):
        options = OutboundPageService.build_product_options(self.outbound_repo, OutboundService)
        OutboundPageService.apply_combo_options(self.product_box, options)

    def load_warehouses(self):
        options = OutboundPageService.build_warehouse_options(self.outbound_repo, OutboundService)
        OutboundPageService.apply_combo_options(self.warehouse_box, options)

    def load_data(self):
        rows = OutboundPageService.build_table_rows(self.outbound_repo, OutboundService)
        OutboundPageService.populate_table(
            self.table,
            rows,
            OutboundService.get_cell_alignment
        )

    def update_stock_display(self):
        OutboundPageService.refresh_stock_label(self, self.outbound_repo, OutboundService)

    # ---------- 页面动作 ----------
    def save_document(self):
        form_raw = OutboundPageService.collect_form_data(self)

        product_id = form_raw["product_id"]
        warehouse_id = form_raw["warehouse_id"]
        qty_text = form_raw["qty_text"]
        price_text = form_raw["price_text"]
        remark = form_raw["remark"]

        try:
            form_data = OutboundService.parse_outbound_form(qty_text, price_text, remark)

            current_stock = self.outbound_repo.get_current_stock(product_id, warehouse_id)
            OutboundService.validate_stock(form_data["qty"], current_stock)

            self.outbound_repo.add_outbound_record(
                product_id,
                warehouse_id,
                form_data["qty"],
                form_data["price"],
                form_data["remark"]
            )

            QMessageBox.information(self, "成功", "出库成功")

            self.prepare_new_document()
            self.load_data()
            self.update_stock_display()

        except ValueError as e:
            QMessageBox.warning(self, "提示", str(e))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"新增出库失败：{e}")

    # ---------- 单据页协议 ----------
    def get_document_title(self) -> str:
        return "出库管理"

    def prepare_new_document(self):
        OutboundPageService.reset_form(self)
        self.update_stock_display()

    def get_document_data(self) -> dict:
        return OutboundPageService.collect_form_data(self)

    def load_document(self, order=None, items=None):
        self.load_data()
        self.update_stock_display()

    def set_read_only_mode(self, read_only: bool):
        OutboundPageService.set_read_only_mode(self, read_only)

    def set_edit_mode(self):
        self.set_read_only_mode(False)

    def supports_save(self) -> bool:
        return True

    def supports_print(self) -> bool:
        return False

    def supports_export_pdf(self) -> bool:
        return False

    def print_preview(self):
        QMessageBox.information(self, "提示", "当前页面暂不支持打印预览")

    def print_document(self):
        QMessageBox.information(self, "提示", "当前页面暂不支持打印")

    def export_to_pdf(self):
        QMessageBox.information(self, "提示", "当前页面暂不支持导出 PDF")
