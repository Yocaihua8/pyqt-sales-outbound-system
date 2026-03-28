from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QMessageBox
)
from PyQt6.QtGui import QPainter, QFont
from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

from datetime import datetime

from src.config.sales_outbound_fields import HEADER_FIELDS, FOOTER_FIELDS

from src.modules.documents.services.sales_outbound_printer import SalesOutboundPrinter
from src.modules.sales.services.sales_outbound_service import SalesOutboundService
from src.modules.master_data.services.company_archive_service import CompanyArchiveService
from src.modules.master_data.services.customer_archive_service import CustomerArchiveService
from src.modules.documents.services.document_form_service import DocumentFormService
from src.modules.documents.services.document_table_service import DocumentTableService
from src.modules.documents.services.document_page_state_service import DocumentPageStateService

from src.modules.documents.ui.base_document_page import BaseDocumentPage


class SalesOutboundPage(BaseDocumentPage):
    back_to_query_requested = pyqtSignal()

    # ---------- 初始化与界面 ----------
    def __init__(self, parent=None):
        super().__init__(parent)

        self.header_widgets = {}
        self.footer_widgets = {}
        self.header_labels = {}
        self.footer_labels = {}

        self.current_company_id = None
        self.current_customer_id = None

        self.create_ui()
        self.load_company_options()
        self.load_customer_options()
        self.init_table_rows()
        self.set_edit_mode()
        self.order_date_input.setText(datetime.now().strftime("%Y-%m-%d"))
        self.prepare_new_document()

    def create_ui(self):
        main_layout = QVBoxLayout(self)

        # ===== 标题 =====
        self.title_label = QLabel("销售出库单")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 26px; font-weight: bold;")
        main_layout.addWidget(self.title_label)

        # ===== 单据头区域 =====
        header_layout = QGridLayout()

        self.customer_selector = QComboBox()

        self.warehouse_input = QLineEdit()
        self.order_no_input = QLineEdit()
        self.order_date_input = QLineEdit()

        self.customer_name_input = QLineEdit()
        self.customer_phone_input = QLineEdit()
        self.customer_address_input = QLineEdit()
        self.customer_contact_input = QLineEdit()
        self.summary_input = QLineEdit()

        self.header_widgets = {
            "warehouse_name": self.warehouse_input,
            "order_no": self.order_no_input,
            "order_date": self.order_date_input,
            "customer_name": self.customer_name_input,
            "customer_phone": self.customer_phone_input,
            "customer_address": self.customer_address_input,
            "customer_contact": self.customer_contact_input,
            "summary_remark": self.summary_input,
        }

        self.header_labels["warehouse_name"] = QLabel("*发货仓库")
        header_layout.addWidget(self.header_labels["warehouse_name"], 0, 0)
        header_layout.addWidget(self.warehouse_input, 0, 1)

        self.header_labels["order_no"] = QLabel("单据编号")
        header_layout.addWidget(self.header_labels["order_no"], 0, 2)
        header_layout.addWidget(self.order_no_input, 0, 3)

        self.header_labels["order_date"] = QLabel("录单日期")
        header_layout.addWidget(self.header_labels["order_date"], 0, 4)
        header_layout.addWidget(self.order_date_input, 0, 5)

        self.header_labels["customer_name"] = QLabel("*购买单位")
        header_layout.addWidget(self.header_labels["customer_name"], 1, 0)
        header_layout.addWidget(self.customer_selector, 1, 1)
        header_layout.addWidget(self.customer_name_input, 1, 2, 1, 2)

        self.header_labels["customer_phone"] = QLabel("单位电话")
        header_layout.addWidget(self.header_labels["customer_phone"], 1, 4)
        header_layout.addWidget(self.customer_phone_input, 1, 5)

        self.header_labels["customer_address"] = QLabel("单位地址")
        header_layout.addWidget(self.header_labels["customer_address"], 2, 0)
        header_layout.addWidget(self.customer_address_input, 2, 1, 1, 3)

        self.header_labels["customer_contact"] = QLabel("联系人")
        header_layout.addWidget(self.header_labels["customer_contact"], 2, 4)
        header_layout.addWidget(self.customer_contact_input, 2, 5)

        self.header_labels["summary_remark"] = QLabel("备注摘要")
        header_layout.addWidget(self.header_labels["summary_remark"], 3, 0)
        header_layout.addWidget(self.summary_input, 3, 1, 1, 5)

        main_layout.addLayout(header_layout)

        # ===== 明细表 =====
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "序号", "商品全名", "规格", "颜色", "件数", "数量", "单价", "金额", "备注"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)

        # 数量、单价变化时自动计算金额
        self.table.itemChanged.connect(self.on_table_item_changed)

        main_layout.addWidget(self.table)

        # ===== 合计区域 =====
        total_layout = QGridLayout()

        self.total_amount_input = QLineEdit()
        self.total_amount_input.setReadOnly(True)

        self.amount_in_words_input = QLineEdit()

        self.footer_labels["total_amount"] = QLabel("金额合计")
        total_layout.addWidget(self.footer_labels["total_amount"], 0, 0)
        total_layout.addWidget(self.total_amount_input, 0, 1)

        self.footer_labels["amount_in_words"] = QLabel("大写金额")
        total_layout.addWidget(self.footer_labels["amount_in_words"], 0, 2)
        total_layout.addWidget(self.amount_in_words_input, 0, 3)

        main_layout.addLayout(total_layout)

        # ===== 公司与签字信息 =====
        footer_layout = QGridLayout()

        self.company_selector = QComboBox()

        self.company_name_input = QLineEdit()
        self.company_phone_input = QLineEdit()
        self.company_address_input = QLineEdit()
        self.company_contact_input = QLineEdit()

        self.company_name_input.textChanged.connect(self.refresh_title)

        self.handler_input = QLineEdit()
        self.recorder_input = QLineEdit()
        self.reviewer_input = QLineEdit()
        self.sign_remark_input = QLineEdit()

        self.footer_widgets = {
            "company_name": self.company_name_input,
            "company_phone": self.company_phone_input,
            "company_address": self.company_address_input,
            "company_contact": self.company_contact_input,
            "handler": self.handler_input,
            "recorder": self.recorder_input,
            "reviewer": self.reviewer_input,
            "sign_remark": self.sign_remark_input,
            "amount_in_words": self.amount_in_words_input,
            "total_amount": self.total_amount_input,
        }

        self.footer_labels["company_name"] = QLabel("公司名称")
        footer_layout.addWidget(self.footer_labels["company_name"], 0, 0)
        footer_layout.addWidget(self.company_selector, 0, 1)
        footer_layout.addWidget(self.company_name_input, 0, 2, 1, 2)

        self.footer_labels["company_phone"] = QLabel("公司电话")
        footer_layout.addWidget(self.footer_labels["company_phone"], 0, 4)
        footer_layout.addWidget(self.company_phone_input, 0, 5)

        self.footer_labels["company_address"] = QLabel("公司地址")
        footer_layout.addWidget(self.footer_labels["company_address"], 1, 0)
        footer_layout.addWidget(self.company_address_input, 1, 1, 1, 3)

        self.footer_labels["company_contact"] = QLabel("联系人")
        footer_layout.addWidget(self.footer_labels["company_contact"], 1, 4)
        footer_layout.addWidget(self.company_contact_input, 1, 5)

        self.footer_labels["handler"] = QLabel("经手人")
        footer_layout.addWidget(self.footer_labels["handler"], 2, 0)
        footer_layout.addWidget(self.handler_input, 2, 1)

        self.footer_labels["recorder"] = QLabel("录单人")
        footer_layout.addWidget(self.footer_labels["recorder"], 2, 2)
        footer_layout.addWidget(self.recorder_input, 2, 3)

        self.footer_labels["reviewer"] = QLabel("审核人")
        footer_layout.addWidget(self.footer_labels["reviewer"], 2, 4)
        footer_layout.addWidget(self.reviewer_input, 2, 5)

        self.footer_labels["sign_remark"] = QLabel("签字备注")
        footer_layout.addWidget(self.footer_labels["sign_remark"], 3, 0)
        footer_layout.addWidget(self.sign_remark_input, 3, 1, 1, 5)

        main_layout.addLayout(footer_layout)

        self.customer_selector.currentIndexChanged.connect(self.on_customer_selected)
        self.company_selector.currentIndexChanged.connect(self.on_company_selected)

        # ===== 操作按钮 =====
        btn_layout = QHBoxLayout()

        self.add_row_btn = QPushButton("新增一行")
        self.add_row_btn.clicked.connect(self.add_row)

        self.delete_row_btn = QPushButton("删除选中行")
        self.delete_row_btn.clicked.connect(self.delete_selected_row)

        self.calc_btn = QPushButton("重新计算合计")
        self.calc_btn.clicked.connect(self.calculate_total_amount)

        self.new_btn = QPushButton("新建单据")
        self.new_btn.clicked.connect(self.prepare_new_document)

        self.save_btn = QPushButton("保存单据")
        self.save_btn.clicked.connect(self.save_document)

        self.preview_btn = QPushButton("打印预览")
        self.preview_btn.clicked.connect(self.print_preview)

        self.back_to_query_btn = QPushButton("返回查询页")
        self.back_to_query_btn.clicked.connect(self.back_to_query_page)

        self.print_btn = QPushButton("打印")
        self.print_btn.clicked.connect(self.print_document)

        btn_layout.addWidget(self.add_row_btn)
        btn_layout.addWidget(self.delete_row_btn)
        btn_layout.addWidget(self.calc_btn)
        btn_layout.addWidget(self.new_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.preview_btn)
        btn_layout.addWidget(self.back_to_query_btn)
        btn_layout.addWidget(self.print_btn)

        self.apply_field_visibility()

        main_layout.addLayout(btn_layout)

    def init_table_rows(self):
        DocumentTableService.init_serial_rows(self.table, row_count=7)

    def apply_field_visibility(self):
        for field in HEADER_FIELDS:
            key = field["key"]
            visible = field.get("visible", True)

            label = self.header_labels.get(key)
            widget = self.header_widgets.get(key)

            if label is not None:
                label.setVisible(visible)
            if widget is not None:
                widget.setVisible(visible)

        for field in FOOTER_FIELDS:
            key = field["key"]
            visible = field.get("visible", True)

            label = self.footer_labels.get(key)
            widget = self.footer_widgets.get(key)

            if label is not None:
                label.setVisible(visible)
            if widget is not None:
                widget.setVisible(visible)

    def refresh_title(self):
        self.title_label.setText(self.get_document_title())

    def get_document_title(self):
        company_name = self.company_name_input.text().strip()
        return f"{company_name}销售出库单" if company_name else "销售出库单"

    def apply_company_profile(self, profile: dict | None = None):
        if profile is None:
            archive = CompanyArchiveService.get_last_used_archive()
            if archive is None:
                CompanyArchiveService.migrate_legacy_profile_if_needed()
                archive = CompanyArchiveService.get_last_used_archive()
            profile = CompanyArchiveService.build_profile_dict(archive)

        self.set_company_profile_fields(profile)
        self.refresh_title()

    def set_company_profile_fields(self, profile: dict):
        DocumentFormService.apply_form_data(
            {
                "company_name": self.company_name_input,
                "company_phone": self.company_phone_input,
                "company_address": self.company_address_input,
                "company_contact": self.company_contact_input,
            },
            profile
        )

    # ---------- 明细表与金额联动 ----------
    def add_row(self):
        DocumentTableService.append_empty_row(self.table)

    def delete_selected_row(self):
        removed = DocumentTableService.remove_current_row(self.table)
        if removed:
            self.calculate_total_amount()

    def refresh_line_no(self):
        DocumentTableService.refresh_serial_numbers(self.table)

    def on_table_item_changed(self, item):
        if item.column() in (5, 6):  # 数量、单价列
            self.calculate_row_amount(item.row())
            self.calculate_total_amount()

    def calculate_row_amount(self, row):
        self.table.blockSignals(True)

        amount = SalesOutboundService.calculate_row_amount_from_table(self.table, row)

        amount_item = self.table.item(row, 7)
        if amount_item is None:
            amount_item = QTableWidgetItem()
            self.table.setItem(row, 7, amount_item)

        amount_item.setText(SalesOutboundService.format_amount(amount))
        amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.table.blockSignals(False)

    def calculate_total_amount(self):
        total = SalesOutboundService.calculate_total_amount_from_table(self.table)
        self.apply_total_amount_patch(
            SalesOutboundService.build_total_amount_patch(total)
        )

    def apply_total_amount_patch(self, patch: dict):
        DocumentFormService.apply_form_data(
            {
                "total_amount": self.footer_widgets["total_amount"],
                "amount_in_words": self.footer_widgets["amount_in_words"],
            },
            patch
        )

    # ---------- 表单数据采集与应用 ----------
    def collect_header_data(self):
        data = DocumentFormService.collect_form_data(
            HEADER_FIELDS,
            self.header_widgets
        )
        data["customer_id"] = self.customer_selector.currentData()
        return data

    def collect_footer_data(self):
        data = DocumentFormService.collect_form_data(
            FOOTER_FIELDS,
            self.footer_widgets
        )
        data["company_id"] = self.company_selector.currentData()
        return data

    def collect_items(self):
        return SalesOutboundService.collect_items_from_table(self.table)

    def get_document_data(self):
        header_data = self.collect_header_data()
        footer_data = self.collect_footer_data()
        items = self.collect_items()

        return SalesOutboundService.build_document_data(
            title=self.get_document_title(),
            header_data=header_data,
            footer_data=footer_data,
            items=items
        )

    def clear_form_fields(self):
        DocumentFormService.clear_multiple_widget_maps(
            [self.header_widgets, self.footer_widgets]
        )

    def apply_form_data(self, form_data: dict):
        DocumentFormService.apply_multiple_form_maps(
            [self.header_widgets, self.footer_widgets],
            form_data
        )

    def rebuild_table_from_items(self, items):
        rows = [
            SalesOutboundService.build_table_row_values(item)
            for item in items
        ]
        DocumentTableService.rebuild_from_rows(self.table, rows)

    def apply_save_result_patch(self, patch: dict):
        DocumentFormService.apply_form_data(
            {
                "order_no": self.header_widgets["order_no"],
                "order_date": self.header_widgets["order_date"],
                "total_amount": self.footer_widgets["total_amount"],
            },
            patch
        )

    # ---------- 单据生命周期 ----------
    def save_document(self):
        self.calculate_total_amount()

        header_data = self.collect_header_data()
        footer_data = self.collect_footer_data()
        items = self.collect_items()

        result = SalesOutboundService.process_save_document(
            header_data=header_data,
            footer_data=footer_data,
            items=items
        )

        patch = result.get("patch")
        if patch:
            self.apply_save_result_patch(patch)

        if result.get("success"):
            CompanyArchiveService.set_last_used_company_id(self.company_selector.currentData())
            CustomerArchiveService.set_last_used_customer_id(self.customer_selector.currentData())

            QMessageBox.information(self, "成功", result.get("message", "保存成功"))
            self.clear_document()
        else:
            QMessageBox.warning(self, "提示", result.get("message", "保存失败"))

    def clear_document(self):
        self.apply_default_archives()

        company_profile = self.collect_company_profile_data()
        customer_profile = self.collect_customer_profile_data()

        patch = SalesOutboundService.build_clear_document_patch(
            current_profile=company_profile,
            current_customer_profile=customer_profile
        )

        self.apply_form_data(patch["header_data"])
        self.apply_form_data(patch["footer_data"])
        DocumentTableService.rebuild_from_rows(self.table, patch["detail_rows"])

        self.set_edit_mode()
        self.refresh_title()

    def collect_company_profile_data(self):
        return DocumentFormService.collect_form_data(
            [
                {"key": "company_name"},
                {"key": "company_phone"},
                {"key": "company_address"},
                {"key": "company_contact"},
            ],
            self.footer_widgets
        )

    def reset_table(self):
        DocumentTableService.clear_and_init(self.table, row_count=7)

    def set_table_row_values(self, row_index: int, values: list):
        DocumentTableService.set_row_values(self.table, row_index, values)

    def load_document(self, order, items):
        self.clear_document()

        order_data = SalesOutboundService.build_order_form_data(order)
        self.apply_form_data(order_data)
        self.rebuild_table_from_items(items)

        self.current_customer_id = order_data.get("customer_id")
        self.current_company_id = order_data.get("company_id")

        self.select_customer_in_combo(self.current_customer_id)
        self.select_company_in_combo(self.current_company_id)

        self.refresh_title()
        self.set_read_only_mode(True)

    def set_read_only_mode(self, read_only: bool):
        DocumentPageStateService.set_read_only_mode(
            header_widgets=self.header_widgets,
            footer_widgets=self.footer_widgets,
            table=self.table,
            back_to_query_btn=self.back_to_query_btn,
            editable_buttons=[
                self.add_row_btn,
                self.delete_row_btn,
                self.save_btn,
            ],
            always_read_only_keys={"total_amount"},
            read_only=read_only,
        )

    def set_edit_mode(self):
        DocumentPageStateService.set_edit_mode(
            header_widgets=self.header_widgets,
            footer_widgets=self.footer_widgets,
            table=self.table,
            back_to_query_btn=self.back_to_query_btn,
            editable_buttons=[
                self.add_row_btn,
                self.delete_row_btn,
                self.save_btn,
            ],
            always_read_only_keys={"total_amount"},
        )

    def back_to_query_page(self):
        self.back_to_query_requested.emit()

    def supports_save(self) -> bool:
        return True

    def supports_print(self) -> bool:
        return True

    def supports_export_pdf(self) -> bool:
        return True

    # ---------- 打印与导出 ----------
    def create_printer(self):
        return SalesOutboundPrinter.create_printer()

    def _draw_cell(self, painter, rect, text="", align=Qt.AlignmentFlag.AlignCenter):
        SalesOutboundPrinter.draw_cell(painter, rect, text, align)

    def draw_sales_order_with_painter(self, painter, printer):
        data = self.get_document_data()
        visibility = self.get_print_visibility_config()

        SalesOutboundPrinter.draw_document(
            painter=painter,
            printer=printer,
            data=data,
            visibility=visibility,
            mm_to_px=self._mm_to_px,
            draw_cell=self._draw_cell,
        )

    def print_preview(self):
        printer = self.create_printer()
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self.paint_sales_order)
        preview.exec()

    def print_document(self):
        printer = self.create_printer()
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self.paint_sales_order(printer)

    def paint_sales_order(self, printer):
        painter = QPainter(printer)
        if not painter.isActive():
            QMessageBox.critical(self, "错误", "无法启动打印绘制。")
            return

        try:
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
            self.draw_sales_order_with_painter(painter, printer)
            painter.restore()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打印预览绘制失败：{e}")
        finally:
            painter.end()

    def _mm_to_px(self, mm, printer):
        return SalesOutboundPrinter.mm_to_px(mm, printer)

    def export_to_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出 PDF",
            f"{self.get_document_title()}.pdf",
            "PDF 文件 (*.pdf)"
        )
        if not file_path:
            return

        if not file_path.lower().endswith(".pdf"):
            file_path += ".pdf"

        try:
            printer = self.create_printer()
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)

            self.paint_sales_order(printer)
            QMessageBox.information(self, "成功", f"PDF 已导出：{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出 PDF 失败：{e}")

    def get_print_visibility_config(self) -> dict:
        return SalesOutboundService.build_print_visibility_config()

    def prepare_new_document(self):
        self.clear_document()

    # ---------- 公司/客户档案选择 ----------
    def load_company_options(self):
        self.company_selector.blockSignals(True)
        self.company_selector.clear()

        options = CompanyArchiveService.get_archive_options()
        for text, value in options:
            self.company_selector.addItem(text, value)

        self.company_selector.blockSignals(False)

    def load_customer_options(self):
        self.customer_selector.blockSignals(True)
        self.customer_selector.clear()

        options = CustomerArchiveService.get_archive_options()
        for text, value in options:
            self.customer_selector.addItem(text, value)

        self.customer_selector.blockSignals(False)

    def on_company_selected(self):
        company_id = self.company_selector.currentData()
        self.current_company_id = company_id

        if company_id is None:
            self.apply_company_profile({})
            return

        archive = CompanyArchiveService.get_archive(company_id)
        profile = CompanyArchiveService.build_profile_dict(archive)
        self.apply_company_profile(profile)

    def on_customer_selected(self):
        customer_id = self.customer_selector.currentData()
        self.current_customer_id = customer_id

        if customer_id is None:
            self.apply_customer_profile({})
            return

        archive = CustomerArchiveService.get_archive(customer_id)
        profile = CustomerArchiveService.build_profile_dict(archive)
        self.apply_customer_profile(profile)

    def apply_customer_profile(self, profile: dict | None = None):
        profile = profile or {}

        DocumentFormService.apply_form_data(
            {
                "customer_name": self.customer_name_input,
                "customer_phone": self.customer_phone_input,
                "customer_address": self.customer_address_input,
                "customer_contact": self.customer_contact_input,
            },
            profile
        )

    def select_company_in_combo(self, company_id: int | None):
        if company_id is None:
            self.company_selector.setCurrentIndex(-1)
            return

        for i in range(self.company_selector.count()):
            if self.company_selector.itemData(i) == company_id:
                self.company_selector.setCurrentIndex(i)
                return

    def select_customer_in_combo(self, customer_id: int | None):
        if customer_id is None:
            self.customer_selector.setCurrentIndex(-1)
            return

        for i in range(self.customer_selector.count()):
            if self.customer_selector.itemData(i) == customer_id:
                self.customer_selector.setCurrentIndex(i)
                return

    def apply_default_archives(self):
        company_archive = CompanyArchiveService.get_last_used_archive()
        if company_archive is None:
            CompanyArchiveService.migrate_legacy_profile_if_needed()
            company_archive = CompanyArchiveService.get_last_used_archive()

        customer_archive = CustomerArchiveService.get_last_used_archive()

        if company_archive is not None:
            self.current_company_id = company_archive.id
            self.select_company_in_combo(company_archive.id)
            self.apply_company_profile(CompanyArchiveService.build_profile_dict(company_archive))
        else:
            self.current_company_id = None
            self.select_company_in_combo(None)
            self.apply_company_profile({})
        if customer_archive is not None:
            self.current_customer_id = customer_archive.id
            self.select_customer_in_combo(customer_archive.id)
            self.apply_customer_profile(CustomerArchiveService.build_profile_dict(customer_archive))
        else:
            self.current_customer_id = None
            self.select_customer_in_combo(None)
            self.apply_customer_profile({})

    def collect_customer_profile_data(self):
        return DocumentFormService.collect_form_data(
            [
                {"key": "customer_name"},
                {"key": "customer_phone"},
                {"key": "customer_address"},
                {"key": "customer_contact"},
            ],
            self.header_widgets
        )
