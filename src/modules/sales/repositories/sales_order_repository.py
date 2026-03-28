from src.DataAccessObjects import db_facade as db_op


class SalesOrderRepository:
    @staticmethod
    def get_sales_order_list():
        return db_op.get_sales_outbound_orders()
