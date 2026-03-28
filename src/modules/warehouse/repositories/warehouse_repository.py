from src.DataAccessObjects import db_facade as db_op


class WarehouseRepository:
    @staticmethod
    def get_warehouses():
        return db_op.get_warehouses()

    @staticmethod
    def warehouse_exists(name: str) -> bool:
        return db_op.warehouse_exists(name)

    @staticmethod
    def add_warehouse(name: str, location: str, remark: str):
        return db_op.add_warehouse(name, location, remark)

    @staticmethod
    def delete_warehouse(warehouse_id: int):
        return db_op.delete_warehouse(warehouse_id)

    @staticmethod
    def get_warehouse_by_name(name: str):
        return db_op.get_warehouse_by_name(name)


    @staticmethod
    def update_warehouse(warehouse_id: int, name: str, location: str, remark: str):
        return db_op.update_warehouse(warehouse_id, name, location, remark)




