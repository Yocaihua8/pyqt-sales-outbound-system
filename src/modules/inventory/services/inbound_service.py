from src.modules.inventory.services.inventory_record_service import InventoryRecordService

class InboundService(InventoryRecordService):

    @staticmethod
    def parse_inbound_form(qty_text: str, price_text: str, remark: str) -> dict:
        return InboundService.parse_common_form(qty_text, price_text, remark)

    @staticmethod
    def parse_form(form_raw: dict) -> dict:
        return InboundService.parse_inbound_form(
            form_raw["qty_text"],
            form_raw["price_text"],
            form_raw["remark"]
        )


