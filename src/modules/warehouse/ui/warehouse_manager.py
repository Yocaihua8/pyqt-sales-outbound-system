from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt

from src.modules.warehouse.services.warehouse_service import WarehouseService


class WarehouseManagerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.editing_warehouse_id = None

        self.create_ui()
        self.load_data()

    def create_ui(self):
        layout = QVBoxLayout(self)

        # 输入区域
        form_layout = QHBoxLayout()

        self.name_input = QLineEdit()
        self.location_input = QLineEdit()
        self.remark_input = QLineEdit()

        form_layout.addWidget(QLabel("仓库名称"))
        form_layout.addWidget(self.name_input)

        form_layout.addWidget(QLabel("仓库位置"))
        form_layout.addWidget(self.location_input)

        form_layout.addWidget(QLabel("备注"))
        form_layout.addWidget(self.remark_input)

        layout.addLayout(form_layout)

        # 按钮区域
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("新增仓库")
        self.add_btn.clicked.connect(self.add_warehouse)

        self.edit_btn = QPushButton("加载编辑")
        self.edit_btn.clicked.connect(self.load_selected_warehouse_to_form)

        self.update_btn = QPushButton("保存修改")
        self.update_btn.clicked.connect(self.update_warehouse)

        self.delete_btn = QPushButton("删除仓库")
        self.delete_btn.clicked.connect(self.delete_warehouse)

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.load_data)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.refresh_btn)

        layout.addLayout(btn_layout)

        # 表格区域
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "仓库名称", "仓库位置", "备注"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

    def render_table_rows(self, table_rows):
        self.table.setRowCount(len(table_rows))

        for row_index, row in enumerate(table_rows):
            for col_index, cell in enumerate(row):
                item = QTableWidgetItem(cell["text"])
                item.setTextAlignment(cell["alignment"])
                self.table.setItem(row_index, col_index, item)

    def load_data(self):
        warehouses = WarehouseService.get_warehouses()
        table_rows = WarehouseService.build_table_rows(warehouses)
        self.render_table_rows(table_rows)

    def collect_form_data(self):
        return WarehouseService.build_warehouse_form_data(
            name=self.name_input.text(),
            location=self.location_input.text(),
            remark=self.remark_input.text(),
        )

    def collect_edit_form_data(self):
        return WarehouseService.build_warehouse_edit_form_data(
            warehouse_id=self.editing_warehouse_id,
            name=self.name_input.text(),
            location=self.location_input.text(),
            remark=self.remark_input.text(),
        )

    def apply_form_data(self, form_data: dict):
        self.name_input.setText(form_data.get("name", ""))
        self.location_input.setText(form_data.get("location", ""))
        self.remark_input.setText(form_data.get("remark", ""))

    def clear_form(self):
        self.editing_warehouse_id = None
        self.name_input.clear()
        self.location_input.clear()
        self.remark_input.clear()

    def get_selected_warehouse(self):
        return WarehouseService.parse_selected_warehouse(self.table)

    def get_selected_warehouse_full(self):
        return WarehouseService.parse_selected_warehouse_full(self.table)

    def load_selected_warehouse_to_form(self):
        selected_warehouse = self.get_selected_warehouse_full()
        if not selected_warehouse:
            QMessageBox.warning(self, "提示", "请先选择一条仓库记录")
            return

        self.editing_warehouse_id = selected_warehouse["id"]
        self.apply_form_data(selected_warehouse)

    def update_warehouse(self):
        form_data = self.collect_edit_form_data()

        ok, result = WarehouseService.validate_warehouse_edit_form(form_data)
        if not ok:
            QMessageBox.warning(
                self,
                "提示",
                WarehouseService.get_warehouse_edit_error_message(result)
            )
            return

        update_result = WarehouseService.update_warehouse(result)
        if update_result.get("success"):
            QMessageBox.information(
                self,
                "成功",
                update_result.get("message", "仓库修改成功")
            )
            self.clear_form()
            self.load_data()
        else:
            QMessageBox.critical(
                self,
                "错误",
                update_result.get("message", "修改仓库失败")
            )

    def add_warehouse(self):
        form_data = self.collect_form_data()

        ok, result = WarehouseService.validate_warehouse_form(form_data)
        if not ok:
            QMessageBox.warning(
                self,
                "提示",
                WarehouseService.get_warehouse_form_error_message(result)
            )
            return

        save_result = WarehouseService.add_warehouse(result)
        if save_result.get("success"):
            QMessageBox.information(self, "成功", save_result.get("message", "仓库新增成功"))
            self.clear_form()
            self.load_data()
        else:
            QMessageBox.critical(self, "错误", save_result.get("message", "新增仓库失败"))

    def delete_warehouse(self):
        selected_warehouse = self.get_selected_warehouse()

        ok, result = WarehouseService.ensure_warehouse_selected(selected_warehouse)
        if not ok:
            QMessageBox.warning(
                self,
                "提示",
                WarehouseService.get_delete_warehouse_message(result)
            )
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            WarehouseService.build_delete_confirm_message(result),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        delete_result = WarehouseService.delete_warehouse(result)
        if delete_result.get("success"):
            QMessageBox.information(
                self,
                "成功",
                delete_result.get("message", "仓库删除成功")
            )
            self.load_data()
        else:
            QMessageBox.critical(
                self,
                "错误",
                delete_result.get("message", "删除仓库失败")
            )




