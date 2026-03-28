from PyQt6.QtWidgets import QTableWidgetItem


class InventoryRecordPageService:
    @staticmethod
    def collect_form_data(page) -> dict:
        return {
            "product_id": page.product_box.currentData(),
            "warehouse_id": page.warehouse_box.currentData(),
            "qty_text": page.qty_input.text().strip(),
            "price_text": page.price_input.text().strip(),
            "remark": page.remark_input.text().strip(),
        }

    @staticmethod
    def build_product_options(record_repo, record_service):
        products = record_repo.get_products()
        return record_service.build_product_options(products)

    @staticmethod
    def build_warehouse_options(record_repo, record_service):
        warehouses = record_repo.get_warehouses()
        return record_service.build_warehouse_options(warehouses)

    @staticmethod
    def apply_combo_options(combo_box, options):
        combo_box.clear()
        for text, value in options:
            combo_box.addItem(text, value)

    @staticmethod
    def reset_form(page):
        page.qty_input.clear()
        page.price_input.clear()
        page.remark_input.clear()
        page.product_box.setCurrentIndex(0)
        page.warehouse_box.setCurrentIndex(0)
        page.qty_input.setFocus()

    @staticmethod
    def set_read_only_mode(page, read_only: bool):
        page.product_box.setEnabled(not read_only)
        page.warehouse_box.setEnabled(not read_only)
        page.qty_input.setReadOnly(read_only)
        page.price_input.setReadOnly(read_only)
        page.remark_input.setReadOnly(read_only)
        page.add_btn.setEnabled(not read_only)

    @staticmethod
    def populate_table(table, rows, alignment_getter):
        table.clearContents()
        table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                item = QTableWidgetItem(value)
                item.setTextAlignment(alignment_getter(col_index))
                table.setItem(row_index, col_index, item)