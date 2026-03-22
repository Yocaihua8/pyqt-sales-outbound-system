from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt

from src.services.product_service import ProductService


class ProductManagerPage(QWidget):
    # ---------- 初始化与界面 ----------
    def __init__(self, parent=None):
        super().__init__(parent)

        self.editing_product_id = None
        self.create_ui()
        self.load_data()

    def create_ui(self):
        layout = QVBoxLayout(self)

        # 输入区域
        form_layout = QHBoxLayout()

        self.name_input = QLineEdit()
        self.spec_input = QLineEdit()
        self.unit_input = QLineEdit()
        self.price_input = QLineEdit()
        self.remark_input = QLineEdit()

        self.price_input.setPlaceholderText("例如：19.9")

        form_layout.addWidget(QLabel("商品名称"))
        form_layout.addWidget(self.name_input)

        form_layout.addWidget(QLabel("规格"))
        form_layout.addWidget(self.spec_input)

        form_layout.addWidget(QLabel("单位"))
        form_layout.addWidget(self.unit_input)

        form_layout.addWidget(QLabel("参考单价"))
        form_layout.addWidget(self.price_input)

        form_layout.addWidget(QLabel("备注"))
        form_layout.addWidget(self.remark_input)

        layout.addLayout(form_layout)

        # 按钮区域
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("新增商品")
        self.add_btn.clicked.connect(self.add_product)

        self.edit_btn = QPushButton("加载编辑")
        self.edit_btn.clicked.connect(self.load_selected_product_to_form)

        self.update_btn = QPushButton("保存修改")
        self.update_btn.clicked.connect(self.update_product)

        self.delete_btn = QPushButton("删除商品")
        self.delete_btn.clicked.connect(self.delete_product)

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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "商品名称", "规格", "单位", "参考单价", "备注"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

    # ---------- 表格展示 ----------
    def render_table_rows(self, table_rows):
        self.table.setRowCount(len(table_rows))

        for row_index, row in enumerate(table_rows):
            for col_index, cell in enumerate(row):
                item = QTableWidgetItem(cell["text"])
                item.setTextAlignment(cell["alignment"])
                self.table.setItem(row_index, col_index, item)

    def load_data(self):
        products = ProductService.get_products()
        table_rows = ProductService.build_table_rows(products)
        self.render_table_rows(table_rows)

    # ---------- 表单采集与清理 ----------
    def collect_form_data(self):
        return ProductService.build_product_form_data(
            name=self.name_input.text(),
            specification=self.spec_input.text(),
            unit=self.unit_input.text(),
            unit_price_text=self.price_input.text(),
            remark=self.remark_input.text(),
        )

    def collect_edit_form_data(self):
        return ProductService.build_product_edit_form_data(
            product_id=self.editing_product_id,
            name=self.name_input.text(),
            specification=self.spec_input.text(),
            unit=self.unit_input.text(),
            unit_price_text=self.price_input.text(),
            remark=self.remark_input.text(),
        )

    def apply_form_data(self, form_data: dict):
        self.name_input.setText(form_data.get("name", ""))
        self.spec_input.setText(form_data.get("specification", ""))
        self.unit_input.setText(form_data.get("unit", ""))
        self.price_input.setText(form_data.get("unit_price_text", ""))
        self.remark_input.setText(form_data.get("remark", ""))

    def clear_form(self):
        self.editing_product_id = None
        self.name_input.clear()
        self.spec_input.clear()
        self.unit_input.clear()
        self.price_input.clear()
        self.remark_input.clear()

    # ---------- 选中项 ----------
    def get_selected_product(self):
        return ProductService.parse_selected_product(self.table)

    def get_selected_product_full(self):
        return ProductService.parse_selected_product_full(self.table)

    # ---------- 商品操作 ----------
    def add_product(self):
        form_data = self.collect_form_data()

        ok, result = ProductService.validate_product_form(form_data)
        if not ok:
            QMessageBox.warning(
                self,
                "提示",
                ProductService.get_product_form_error_message(result)
            )
            return

        save_result = ProductService.add_product(result)
        if save_result.get("success"):
            QMessageBox.information(self, "成功", save_result.get("message", "商品新增成功"))
            self.clear_form()
            self.load_data()
        else:
            QMessageBox.critical(self, "错误", save_result.get("message", "新增商品失败"))

    def delete_product(self):
        selected_product = self.get_selected_product()

        ok, result = ProductService.ensure_product_selected(selected_product)
        if not ok:
            QMessageBox.warning(
                self,
                "提示",
                ProductService.get_delete_product_message(result)
            )
            return

        reply = QMessageBox.question(
            self,
            "确认删除",
            ProductService.build_delete_confirm_message(result),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        delete_result = ProductService.delete_product(result)
        if delete_result.get("success"):
            QMessageBox.information(
                self,
                "成功",
                delete_result.get("message", "商品删除成功")
            )
            self.load_data()
        else:
            QMessageBox.critical(
                self,
                "错误",
                delete_result.get("message", "删除商品失败")
            )

    def load_selected_product_to_form(self):
        selected_product = self.get_selected_product_full()
        if not selected_product:
            QMessageBox.warning(self, "提示", "请先选择一条商品记录")
            return

        self.editing_product_id = selected_product["id"]
        self.apply_form_data(selected_product)

    def update_product(self):
        form_data = self.collect_edit_form_data()

        ok, result = ProductService.validate_product_edit_form(form_data)
        if not ok:
            QMessageBox.warning(
                self,
                "提示",
                ProductService.get_product_edit_error_message(result)
            )
            return

        update_result = ProductService.update_product(result)
        if update_result.get("success"):
            QMessageBox.information(
                self,
                "成功",
                update_result.get("message", "商品修改成功")
            )
            self.clear_form()
            self.load_data()
        else:
            QMessageBox.critical(
                self,
                "错误",
                update_result.get("message", "修改商品失败")
            )
