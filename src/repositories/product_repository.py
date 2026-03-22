from src.DataAccessObjects import db_operations as db_op


class ProductRepository:
    @staticmethod
    def get_products():
        return db_op.get_products()

    @staticmethod
    def product_exists(name: str) -> bool:
        return db_op.product_exists(name)

    @staticmethod
    def get_product_by_name(name: str):
        return db_op.get_product_by_name(name)

    @staticmethod
    def add_product(name: str, specification: str, unit: str, unit_price: float, remark: str):
        return db_op.add_product(name, specification, unit, unit_price, remark)

    @staticmethod
    def delete_product(product_id: int):
        return db_op.delete_product(product_id)

    @staticmethod
    def update_product(product_id: int, name: str, specification: str, unit: str, unit_price: float, remark: str):
        return db_op.update_product(product_id, name, specification, unit, unit_price, remark)




