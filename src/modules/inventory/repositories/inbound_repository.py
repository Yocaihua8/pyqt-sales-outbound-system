from src.DataAccessObjects import db_facade as db_op


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

    def add_record(self, form_raw: dict, form_data: dict):
        return self.add_inbound_record(
            form_raw["product_id"],
            form_raw["warehouse_id"],
            form_data["qty"],
            form_data["price"],
            form_data["remark"]
        )

    def get_records(self):
        return self.get_inbound_records()

