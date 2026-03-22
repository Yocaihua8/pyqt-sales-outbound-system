from PyQt6.QtWidgets import QMessageBox

from src.services.sales_outbound_service import SalesOutboundService


class SalesOutboundDetailController:
    def __init__(self, parent_window, sales_outbound_page, open_form_page):
        self.parent_window = parent_window
        self.sales_outbound_page = sales_outbound_page
        self.open_form_page = open_form_page

    def _load_order_data(self, order_id: int):
        try:
            order, items = SalesOutboundService.get_order_with_items(order_id)
        except Exception as e:
            QMessageBox.critical(self.parent_window, "错误", f"读取单据失败：{e}")
            return None, None

        if not order:
            QMessageBox.warning(self.parent_window, "提示", f"未找到单据 ID: {order_id}")
            return None, None

        return order, items

    def _show_detail_page(self, order, items):
        self.sales_outbound_page.load_document(order, items)
        self.sales_outbound_page.set_read_only_mode(True)
        self.open_form_page("sales_outbound", "销售出库单", self.sales_outbound_page)

    def _preview_if_needed(self, preview_print: bool):
        if preview_print:
            self.sales_outbound_page.print_preview()

    def open_detail(self, order_id: int, preview_print: bool = False):
        order, items = self._load_order_data(order_id)
        if not order:
            return

        self._show_detail_page(order, items)
        self._preview_if_needed(preview_print)