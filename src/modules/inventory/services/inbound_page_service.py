from src.modules.inventory.services.inventory_record_page_service import InventoryRecordPageService


class InboundPageService(InventoryRecordPageService):
    @staticmethod
    def build_table_rows(inbound_repo, inbound_service):
        records = inbound_repo.get_records()
        products = inbound_repo.get_products()
        warehouses = inbound_repo.get_warehouses()

        product_map = {p[0]: p[1] for p in products}
        warehouse_map = {w[0]: w[1] for w in warehouses}

        return inbound_service.build_record_table_rows(records, product_map, warehouse_map)
