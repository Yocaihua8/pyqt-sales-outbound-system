from src.modules.inventory.services.inventory_record_service import InventoryRecordService

class OutboundService(InventoryRecordService):
    @staticmethod
    def parse_outbound_form(qty_text: str, price_text: str, remark: str) -> dict:
        return OutboundService.parse_common_form(qty_text, price_text, remark)

    @staticmethod
    def validate_stock(qty: float, current_stock: float):
        if qty > current_stock:
            raise ValueError(f"当前库存 {current_stock}，无法出库 {qty}")

    @staticmethod
    def format_stock_text(stock):
        return f"当前库存: {stock}"

    @staticmethod
    def parse_form(form_raw: dict) -> dict:
        return OutboundService.parse_outbound_form(
            form_raw["qty_text"],
            form_raw["price_text"],
            form_raw["remark"]
        )
