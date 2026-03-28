from typing import List, Tuple, Any

from PyQt6.QtCore import Qt


class InventoryRecordService:
    @staticmethod
    def parse_common_form(qty_text: str, price_text: str, remark: str) -> dict:
        qty_text = qty_text.strip()
        price_text = price_text.strip()
        remark = remark.strip()

        if not qty_text:
            raise ValueError("数量不能为空")
        if not price_text:
            raise ValueError("单价不能为空")

        try:
            qty = float(qty_text)
        except ValueError:
            raise ValueError("数量格式不正确")

        try:
            price = float(price_text)
        except ValueError:
            raise ValueError("单价格式不正确")

        if qty <= 0:
            raise ValueError("数量必须大于 0")
        if price < 0:
            raise ValueError("单价不能小于 0")

        return {
            "qty": qty,
            "price": price,
            "remark": remark
        }

    @staticmethod
    def build_product_options(products):
        return [(p[1], p[0]) for p in products]

    @staticmethod
    def build_warehouse_options(warehouses):
        return [(w[1], w[0]) for w in warehouses]

    @staticmethod
    def build_record_table_rows(records, product_map, warehouse_map):
        rows = []

        for r in records:
            row = [
                "" if r.id is None else str(r.id),
                product_map.get(r.product_id, f"商品ID:{r.product_id}"),
                warehouse_map.get(r.warehouse_id, f"仓库ID:{r.warehouse_id}"),
                "" if r.quantity is None else str(r.quantity),
                "" if r.unit_price is None else str(r.unit_price),
                "" if r.total_amount is None else str(r.total_amount),
                "" if r.created_at is None else str(r.created_at),
            ]
            rows.append(row)

        return rows

    @staticmethod
    def get_cell_alignment(col_index: int):
        if col_index in (3, 4, 5):
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return Qt.AlignmentFlag.AlignCenter