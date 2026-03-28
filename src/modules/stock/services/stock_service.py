from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

import csv

from src.core.constants import LOW_STOCK_THRESHOLD, LOW_STOCK_SUFFIX
from src.modules.stock.repositories.stock_repository import StockRepository


class StockService:
    @staticmethod
    def get_low_stock_threshold() -> int:
        return LOW_STOCK_THRESHOLD

    @staticmethod
    def get_low_stock_suffix() -> str:
        return LOW_STOCK_SUFFIX

    @staticmethod
    def get_low_stock_background():
        return QColor(255, 220, 220)

    @staticmethod
    def is_low_stock(stock_qty) -> bool:
        try:
            return float(stock_qty) <= StockService.get_low_stock_threshold()
        except (TypeError, ValueError):
            return False

    @staticmethod
    def format_cell_text(value, col_index: int, stock_qty) -> str:
        if col_index == 4 and StockService.is_low_stock(stock_qty):
            return f"{stock_qty}{StockService.get_low_stock_suffix()}"
        return "" if value is None else str(value)

    @staticmethod
    def get_row_background(stock_qty):
        if StockService.is_low_stock(stock_qty):
            return StockService.get_low_stock_background()
        return None

    @staticmethod
    def get_stock_summary(
            product_name: str = "",
            warehouse_name: str = "",
            low_stock_only: bool = False,
            low_stock_threshold: int = LOW_STOCK_THRESHOLD
    ):
        return StockRepository.get_stock_summary(
            product_name=product_name,
            warehouse_name=warehouse_name,
            low_stock_only=low_stock_only,
            low_stock_threshold=low_stock_threshold
        )

    @staticmethod
    def build_stock_filters(product_name, warehouse_name, low_stock_only=False):
        return {
            "product_name": str(product_name or "").strip(),
            "warehouse_name": str(warehouse_name or "").strip(),
            "low_stock_only": bool(low_stock_only),
            "low_stock_threshold": StockService.get_low_stock_threshold(),
        }

    @staticmethod
    def get_cell_alignment(col_index: int):
        if col_index >= 2:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return Qt.AlignmentFlag.AlignCenter

    @staticmethod
    def get_stock_qty(row) -> float:
        value = row[4] if len(row) > 4 else 0
        return value if value is not None else 0

    @staticmethod
    def build_table_rows(data):
        table_rows = []

        for row in data:
            stock_qty = StockService.get_stock_qty(row)
            background = StockService.get_row_background(stock_qty)

            formatted_row = []
            for col_index, value in enumerate(row):
                formatted_row.append({
                    "text": StockService.format_cell_text(value, col_index, stock_qty),
                    "alignment": StockService.get_cell_alignment(col_index),
                    "background": background,
                })

            table_rows.append(formatted_row)

        return table_rows

    @staticmethod
    def get_stock_table_headers():
        return ["商品名称", "仓库名称", "总入库", "总出库", "当前库存"]

    @staticmethod
    def build_export_rows(data):
        rows = []
        for row in data:
            rows.append([
                "" if value is None else str(value)
                for value in row
            ])
        return rows

    @staticmethod
    def export_stock_to_csv(file_path: str, data):
        file_path = str(file_path or "").strip()
        if not file_path:
            raise ValueError("导出文件路径不能为空")

        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        rows = StockService.build_export_rows(data)

        with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(StockService.get_stock_table_headers())
            writer.writerows(rows)

        return file_path


