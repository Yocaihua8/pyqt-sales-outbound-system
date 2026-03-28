from src.modules.inventory.services.inventory_record_page_service import InventoryRecordPageService


class OutboundPageService(InventoryRecordPageService):
    @staticmethod
    def build_table_rows(outbound_repo, outbound_service):
        records = outbound_repo.get_records()
        products = outbound_repo.get_products()
        warehouses = outbound_repo.get_warehouses()

        product_map = {p[0]: p[1] for p in products}
        warehouse_map = {w[0]: w[1] for w in warehouses}

        return outbound_service.build_record_table_rows(records, product_map, warehouse_map)

    @staticmethod
    def refresh_stock_label(page, outbound_repo, outbound_service):
        product_id = page.product_box.currentData()
        warehouse_id = page.warehouse_box.currentData()

        if product_id is None or warehouse_id is None:
            page.stock_label.setText("当前库存: -")
            return

        stock = outbound_repo.get_current_stock(product_id, warehouse_id)
        page.stock_label.setText(outbound_service.format_stock_text(stock))
