from PyQt6.QtCore import Qt


class SalesOrderListService:
    @staticmethod
    def format_amount(value) -> str:
        if value is None:
            return ""
        return f"{float(value):.2f}"

    @staticmethod
    def get_cell_alignment(col_index: int):
        if col_index == 5:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        if col_index == 0:
            return Qt.AlignmentFlag.AlignCenter
        return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

    @staticmethod
    def build_order_table_rows(orders):
        rows = []

        for order in orders:
            row = [
                "" if order[0] is None else str(order[0]),
                "" if order[1] is None else str(order[1]),
                "" if order[2] is None else str(order[2]),
                "" if order[4] is None else str(order[4]),
                "" if order[3] is None else str(order[3]),
                SalesOrderListService.format_amount(order[5]),
            ]
            rows.append(row)

        return rows