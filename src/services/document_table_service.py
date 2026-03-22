from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt


class DocumentTableService:
    @staticmethod
    def build_cell(value, col_index: int) -> QTableWidgetItem:
        cell = QTableWidgetItem("" if value is None else str(value))

        if col_index == 0:
            cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        elif col_index in (4, 5, 6, 7):
            cell.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        else:
            cell.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        return cell

    @staticmethod
    def set_row_values(table: QTableWidget, row_index: int, values: list):
        table.insertRow(row_index)

        for col_index, value in enumerate(values):
            table.setItem(row_index, col_index, DocumentTableService.build_cell(value, col_index))

    @staticmethod
    def init_serial_rows(table: QTableWidget, row_count: int = 7):
        table.setRowCount(row_count)

        for row in range(row_count):
            sn_item = QTableWidgetItem(str(row + 1))
            sn_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 0, sn_item)

    @staticmethod
    def append_empty_row(table: QTableWidget):
        row = table.rowCount()
        table.insertRow(row)

        sn_item = QTableWidgetItem(str(row + 1))
        sn_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, 0, sn_item)

    @staticmethod
    def remove_current_row(table: QTableWidget) -> bool:
        current_row = table.currentRow()
        if current_row == -1:
            return False

        table.blockSignals(True)
        table.removeRow(current_row)
        DocumentTableService.refresh_serial_numbers(table)
        table.blockSignals(False)
        return True

    @staticmethod
    def refresh_serial_numbers(table: QTableWidget):
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item is None:
                item = QTableWidgetItem()
                table.setItem(row, 0, item)

            item.setText(str(row + 1))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    @staticmethod
    def clear_and_init(table: QTableWidget, row_count: int = 7):
        table.setRowCount(0)
        DocumentTableService.init_serial_rows(table, row_count=row_count)

    @staticmethod
    def rebuild_from_rows(table: QTableWidget, rows: list[list]):
        table.setRowCount(0)

        for row_index, values in enumerate(rows):
            DocumentTableService.set_row_values(table, row_index, values)