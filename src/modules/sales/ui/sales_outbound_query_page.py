from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QDateEdit, QApplication
)
from PyQt6.QtCore import Qt, QDate
from src.modules.sales.services.sales_outbound_service import SalesOutboundService


class SalesOutboundQueryPage(QWidget):
    # ---------- 初始化 ----------
    def __init__(self, parent=None, order_detail_opener=None):
        super().__init__(parent)
        self.current_order_id = None
        self.order_detail_opener = order_detail_opener
        self.create_ui()
        self.query_orders()

    def create_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel("销售出库单查询")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 8px;")
        main_layout.addWidget(title)

        # 查询区
        search_layout = QHBoxLayout()

        self.order_no_input = QLineEdit()
        self.order_no_input.setPlaceholderText("单据编号")

        self.customer_name_input = QLineEdit()
        self.customer_name_input.setPlaceholderText("客户名称")

        self.start_date_input = QDateEdit()
        self.start_date_input.setDisplayFormat("yyyy-MM-dd")
        self.start_date_input.setCalendarPopup(True)

        self.end_date_input = QDateEdit()
        self.end_date_input.setDisplayFormat("yyyy-MM-dd")
        self.end_date_input.setCalendarPopup(True)

        self.query_btn = QPushButton("查询")
        self.reset_btn = QPushButton("重置")
        self.view_btn = QPushButton("查看详情")
        self.reprint_btn = QPushButton("重新打印")
        self.today_btn = QPushButton("今天")
        self.this_month_btn = QPushButton("本月")
        self.all_btn = QPushButton("全部")
        self.refresh_btn = QPushButton("刷新")
        self.copy_order_no_btn = QPushButton("复制单号")

        search_layout.addWidget(QLabel("单据编号"))
        search_layout.addWidget(self.order_no_input)

        search_layout.addWidget(QLabel("客户名称"))
        search_layout.addWidget(self.customer_name_input)

        search_layout.addWidget(QLabel("开始日期"))
        search_layout.addWidget(self.start_date_input)

        search_layout.addWidget(QLabel("结束日期"))
        search_layout.addWidget(self.end_date_input)

        search_layout.addWidget(self.today_btn)
        search_layout.addWidget(self.this_month_btn)
        search_layout.addWidget(self.all_btn)
        search_layout.addWidget(self.query_btn)
        search_layout.addWidget(self.reset_btn)
        search_layout.addWidget(self.refresh_btn)
        search_layout.addWidget(self.copy_order_no_btn)
        search_layout.addWidget(self.view_btn)
        search_layout.addWidget(self.reprint_btn)

        main_layout.addLayout(search_layout)

        # 列表区
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "单据编号", "录单日期", "发货仓库", "客户名称", "金额合计"
        ])
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)

        main_layout.addWidget(self.table)

        self.query_btn.clicked.connect(self.query_orders)
        self.reset_btn.clicked.connect(self.reset_query)
        self.view_btn.clicked.connect(self.view_order)
        self.reprint_btn.clicked.connect(self.reprint_order)
        self.table.cellDoubleClicked.connect(self.handle_double_click)
        self.today_btn.clicked.connect(self.set_today_range)
        self.this_month_btn.clicked.connect(self.set_this_month_range)
        self.all_btn.clicked.connect(self.set_all_range)
        self.refresh_btn.clicked.connect(self.query_orders)
        self.copy_order_no_btn.clicked.connect(self.copy_order_no)
        self.apply_named_date_range("this_month", auto_query=False)

    def prepare_page(self):
        self.query_orders()

    # ---------- 查询条件 ----------
    def collect_query_filters(self):
        return SalesOutboundService.build_query_filters(
            order_no=self.order_no_input.text(),
            customer_name=self.customer_name_input.text(),
            start_date=self.start_date_input.date().toString("yyyy-MM-dd"),
            end_date=self.end_date_input.date().toString("yyyy-MM-dd"),
        )

    def apply_date_range(self, start_date: str, end_date: str, auto_query=True):
        self.start_date_input.setDate(QDate.fromString(start_date, "yyyy-MM-dd"))
        self.end_date_input.setDate(QDate.fromString(end_date, "yyyy-MM-dd"))

        if auto_query:
            self.query_orders()

    def apply_named_date_range(self, range_type: str, auto_query=True):
        date_range = SalesOutboundService.build_query_date_range(range_type)
        self.apply_date_range(
            date_range["start_date"],
            date_range["end_date"],
            auto_query=auto_query
        )

    # ---------- 查询执行 ----------
    def query_orders(self):
        filters = self.collect_query_filters()

        try:
            rows = SalesOutboundService.build_query_table_rows(**filters)
        except ValueError as e:
            QMessageBox.warning(self, "提示", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "错误", f"查询失败：{e}")
            return

        self.table.setRowCount(0)

        for row_index, row_data in enumerate(rows):
            self.table.insertRow(row_index)
            for col_index, text in enumerate(row_data):
                item = QTableWidgetItem(text)
                item.setTextAlignment(
                    SalesOutboundService.get_query_cell_alignment(col_index)
                )
                self.table.setItem(row_index, col_index, item)

    def reset_query(self):
        self.order_no_input.clear()
        self.customer_name_input.clear()
        self.apply_named_date_range("this_month")

    # ---------- 单据动作 ----------
    def get_selected_order_id(self):
        return SalesOutboundService.parse_selected_order_id(self.table)

    def get_selected_order_no(self):
        return SalesOutboundService.parse_selected_order_no(self.table)

    def _open_order_detail(self, order_id, preview_print=False):
        if self.order_detail_opener is None:
            action_text = "打印预览" if preview_print else "详情页"
            QMessageBox.critical(self, "错误", f"未配置详情打开入口，无法打开{action_text}")
            return

        self.order_detail_opener(order_id, preview_print=preview_print)

    def open_selected_order(self, preview_print=False):
        try:
            order_id = SalesOutboundService.ensure_order_selected(
                self.get_selected_order_id()
            )
        except ValueError as e:
            QMessageBox.warning(self, "提示", str(e))
            return

        self._open_order_detail(order_id, preview_print=preview_print)

    def view_order(self):
        self.open_selected_order(preview_print=False)

    def reprint_order(self):
        self.open_selected_order(preview_print=True)

    def copy_order_no(self):
        try:
            order_no = SalesOutboundService.ensure_text_selected(
                self.get_selected_order_no()
            )
        except ValueError as e:
            QMessageBox.warning(self, "提示", str(e))
            return

        clipboard = QApplication.clipboard()
        clipboard.setText(order_no)
        QMessageBox.information(self, "提示", f"单号已复制：{order_no}")

    def handle_double_click(self, _row, _column):
        self.open_selected_order(preview_print=False)

    # ---------- 日期范围快捷操作 ----------
    def set_today_range(self):
        self.apply_named_date_range("today")

    def set_this_month_range(self):
        self.apply_named_date_range("this_month")

    def set_all_range(self):
        self.apply_named_date_range("all")
