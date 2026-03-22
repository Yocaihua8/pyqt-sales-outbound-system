from src.DataAccessObjects import db_operations as db_op
from src.core.constants import LOW_STOCK_THRESHOLD


class StockRepository:
    @staticmethod
    def get_stock_summary(
        product_name: str = "",
        warehouse_name: str = "",
        low_stock_only: bool = False,
        low_stock_threshold: int = LOW_STOCK_THRESHOLD
    ):
        return db_op.get_stock_summary(
            product_name=product_name,
            warehouse_name=warehouse_name,
            low_stock_only=low_stock_only,
            low_stock_threshold=low_stock_threshold
        )