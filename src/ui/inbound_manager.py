from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView
)

from src.repositories.inbound_repository import InboundRepository
from src.services.inbound_service import InboundService
from src.services.inbound_page_service import InboundPageService
from src.ui.base_document_page import BaseDocumentPage


class InboundManagerPage(BaseDocumentPage):
    # ---------- 初始化与界面 ----------
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inbound_repo = InboundRepository()

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

    # ---------- 页面初始化数据 ----------
    def load_products(self):
        options = InboundPageService.build_product_options(self.inbound_repo, InboundService)
        InboundPageService.apply_combo_options(self.product_box, options)

    def load_warehouses(self):
        options = InboundPageService.build_warehouse_options(self.inbound_repo, InboundService)
        InboundPageService.apply_combo_options(self.warehouse_box, options)

    def load_data(self):
        rows = InboundPageService.build_table_rows(self.inbound_repo, InboundService)
        InboundPageService.populate_table(
            self.table,
            rows,
            InboundService.get_cell_alignment
        )

    # ---------- 页面动作 ----------
    def save_document(self):
        form_raw = InboundPageService.collect_form_data(self)

        product_id = form_raw["product_id"]
        warehouse_id = form_raw["warehouse_id"]
        qty_text = form_raw["qty_text"]
        price_text = form_raw["price_text"]
        remark = form_raw["remark"]

        try:
            form_data = InboundService.parse_inbound_form(qty_text, price_text, remark)

            self.inbound_repo.add_inbound_record(
                product_id,
                warehouse_id,
                form_data["qty"],
                form_data["price"],
                form_data["remark"]
            )

            QMessageBox.information(self, "成功", "入库成功")

            self.prepare_new_document()
            self.load_data()

        except ValueError as e:
            QMessageBox.warning(self, "提示", str(e))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"新增入库失败：{e}")

    # ---------- 单据页协议 ----------
    def get_document_title(self) -> str:
        return "入库管理"

    def prepare_new_document(self):
        InboundPageService.reset_form(self)

    def get_document_data(self) -> dict:
        return InboundPageService.collect_form_data(self)

    def load_document(self, order=None, items=None):
        # 当前入库页还不是详情型单据页，先占位
        self.load_data()

    def set_read_only_mode(self, read_only: bool):
        InboundPageService.set_read_only_mode(self, read_only)

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
