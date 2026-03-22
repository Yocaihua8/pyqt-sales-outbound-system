from src.DataAccessObjects import db_operations as db_op


class InboundRepository:
    @staticmethod
    def get_products():
        return db_op.get_products()

    @staticmethod
    def get_warehouses():
        return db_op.get_warehouses()

    @staticmethod
    def get_inbound_records():
        return db_op.get_inbound_records()

    @staticmethod
    def add_inbound_record(product_id, warehouse_id, qty, price, remark):
        return db_op.add_inbound_record(product_id, warehouse_id, qty, price, remark)