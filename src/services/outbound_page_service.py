from PyQt6.QtWidgets import QTableWidgetItem


class OutboundPageService:
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
    def build_table_rows(outbound_repo, outbound_service):
        records = outbound_repo.get_outbound_records()
        products = outbound_repo.get_products()
        warehouses = outbound_repo.get_warehouses()

        product_map = {p[0]: p[1] for p in products}
        warehouse_map = {w[0]: w[1] for w in warehouses}

        return outbound_service.build_record_table_rows(records, product_map, warehouse_map)

    @staticmethod
    def build_product_options(outbound_repo, outbound_service):
        products = outbound_repo.get_products()
        return outbound_service.build_product_options(products)

    @staticmethod
    def build_warehouse_options(outbound_repo, outbound_service):
        warehouses = outbound_repo.get_warehouses()
        return outbound_service.build_warehouse_options(warehouses)

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

    @staticmethod
    def refresh_stock_label(page, outbound_repo, outbound_service):
        product_id = page.product_box.currentData()
        warehouse_id = page.warehouse_box.currentData()

        if product_id is None or warehouse_id is None:
            page.stock_label.setText("当前库存: -")
            return

        stock = outbound_repo.get_current_stock(product_id, warehouse_id)
        page.stock_label.setText(outbound_service.format_stock_text(stock))