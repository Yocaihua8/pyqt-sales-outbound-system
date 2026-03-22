from src.DataAccessObjects import db_operations as db_op


class SalesOutboundRepository:
    @staticmethod
    def get_orders(order_no="", customer_name="", start_date="", end_date=""):
        return db_op.get_sales_outbound_orders(
            order_no=order_no,
            customer_name=customer_name,
            start_date=start_date,
            end_date=end_date
        )

    @staticmethod
    def get_order_with_items(order_id: int):
        return db_op.get_sales_outbound_order_with_items(order_id)

    @staticmethod
    def save_order_document(order, items):
        return db_op.save_sales_outbound_document(order, items)