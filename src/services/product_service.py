from src.repositories.product_repository import ProductRepository


class ProductService:
    @staticmethod
    def get_products():
        return ProductRepository.get_products()

    @staticmethod
    def get_table_cell_text(value, col_index: int) -> str:
        if value is None:
            return ""
        if col_index == 4:
            try:
                return f"{float(value):.2f}"
            except (TypeError, ValueError):
                return ""
        return str(value)

    @staticmethod
    def get_table_cell_alignment(col_index: int):
        from PyQt6.QtCore import Qt
        if col_index == 4:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return Qt.AlignmentFlag.AlignCenter

    @staticmethod
    def build_table_rows(products):
        table_rows = []

        for row in products:
            formatted_row = []
            for col_index, value in enumerate(row):
                formatted_row.append({
                    "text": ProductService.get_table_cell_text(value, col_index),
                    "alignment": ProductService.get_table_cell_alignment(col_index),
                })
            table_rows.append(formatted_row)

        return table_rows

    @staticmethod
    def build_product_form_data(name, specification, unit, unit_price_text, remark):
        return {
            "name": str(name or "").strip(),
            "specification": str(specification or "").strip(),
            "unit": str(unit or "").strip(),
            "unit_price_text": str(unit_price_text or "").strip(),
            "remark": str(remark or "").strip(),
        }

    @staticmethod
    def validate_product_form(form_data: dict):
        name = form_data["name"]
        unit_price_text = form_data["unit_price_text"]

        if not name:
            return False, {"error": "missing_name"}

        if ProductRepository.product_exists(name):
            return False, {"error": "duplicate_name"}

        try:
            unit_price = float(unit_price_text) if unit_price_text else 0.0
        except ValueError:
            return False, {"error": "invalid_price"}

        result = dict(form_data)
        result["unit_price"] = unit_price
        return True, result

    @staticmethod
    def get_product_form_error_message(result: dict) -> str:
        error = result.get("error")
        if error == "missing_name":
            return "商品名称不能为空"
        if error == "duplicate_name":
            return "商品名称已存在"
        if error == "invalid_price":
            return "参考单价必须是数字"
        return "商品数据校验失败"

    @staticmethod
    def add_product(form_data: dict) -> dict:
        try:
            ProductRepository.add_product(
                form_data["name"],
                form_data["specification"],
                form_data["unit"],
                form_data["unit_price"],
                form_data["remark"],
            )
            return {"success": True, "message": "商品新增成功"}
        except Exception as e:
            return {"success": False, "message": f"新增商品失败：{e}"}

    @staticmethod
    def parse_selected_product(table):
        current_row = table.currentRow()
        if current_row < 0:
            return None

        id_item = table.item(current_row, 0)
        name_item = table.item(current_row, 1)

        if id_item is None:
            return None

        product_id_text = id_item.text().strip()
        product_name = name_item.text().strip() if name_item else ""

        if not product_id_text:
            return None

        try:
            product_id = int(product_id_text)
        except ValueError:
            return None

        return {
            "id": product_id,
            "name": product_name,
            "row": current_row,
        }

    @staticmethod
    def ensure_product_selected(selected_product):
        if not selected_product:
            return False, {"error": "no_selection"}
        return True, selected_product

    @staticmethod
    def get_delete_product_message(result: dict) -> str:
        error = result.get("error")
        if error == "no_selection":
            return "请先选择一条商品记录"
        return "删除商品失败"

    @staticmethod
    def build_delete_confirm_message(selected_product: dict) -> str:
        product_name = selected_product.get("name", "").strip()
        if product_name:
            return f"确定删除商品“{product_name}”吗？"
        return "确定删除当前选中的商品吗？"

    @staticmethod
    def delete_product(selected_product: dict) -> dict:
        try:
            ProductRepository.delete_product(selected_product["id"])
            return {
                "success": True,
                "message": "商品删除成功"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"删除商品失败：{e}"
            }

    @staticmethod
    def build_product_edit_form_data(product_id, name, specification, unit, unit_price_text, remark):
        return {
            "id": product_id,
            "name": str(name or "").strip(),
            "specification": str(specification or "").strip(),
            "unit": str(unit or "").strip(),
            "unit_price_text": str(unit_price_text or "").strip(),
            "remark": str(remark or "").strip(),
        }

    @staticmethod
    def parse_selected_product_full(table):
        current_row = table.currentRow()
        if current_row < 0:
            return None

        values = []
        for col in range(table.columnCount()):
            item = table.item(current_row, col)
            values.append(item.text().strip() if item else "")

        try:
            product_id = int(values[0]) if values[0] else None
        except ValueError:
            return None

        if not product_id:
            return None

        return {
            "id": product_id,
            "name": values[1],
            "specification": values[2],
            "unit": values[3],
            "unit_price_text": values[4],
            "remark": values[5],
        }

    @staticmethod
    def is_duplicate_name_for_edit(product_id: int, name: str) -> bool:
        existing = ProductRepository.get_product_by_name(name)
        if not existing:
            return False
        return existing.id != product_id

    @staticmethod
    def validate_product_edit_form(form_data: dict):
        product_id = form_data.get("id")
        name = form_data.get("name", "")
        unit_price_text = form_data.get("unit_price_text", "")

        if not product_id:
            return False, {"error": "missing_id"}

        if not name:
            return False, {"error": "missing_name"}

        if ProductService.is_duplicate_name_for_edit(product_id, name):
            return False, {"error": "duplicate_name"}

        try:
            unit_price = float(unit_price_text) if unit_price_text else 0.0
        except ValueError:
            return False, {"error": "invalid_price"}

        result = dict(form_data)
        result["unit_price"] = unit_price
        return True, result

    @staticmethod
    def get_product_edit_error_message(result: dict) -> str:
        error = result.get("error")
        if error == "missing_id":
            return "请先选择一条商品记录"
        if error == "missing_name":
            return "商品名称不能为空"
        if error == "duplicate_name":
            return "商品名称已存在"
        if error == "invalid_price":
            return "参考单价必须是数字"
        return "商品编辑数据校验失败"

    @staticmethod
    def update_product(form_data: dict) -> dict:
        try:
            ProductRepository.update_product(
                form_data["id"],
                form_data["name"],
                form_data["specification"],
                form_data["unit"],
                form_data["unit_price"],
                form_data["remark"],
            )
            return {"success": True, "message": "商品修改成功"}
        except Exception as e:
            return {"success": False, "message": f"修改商品失败：{e}"}