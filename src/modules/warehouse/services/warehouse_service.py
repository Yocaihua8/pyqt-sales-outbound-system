from PyQt6.QtCore import Qt

from src.modules.warehouse.repositories.warehouse_repository import WarehouseRepository


class WarehouseService:
    @staticmethod
    def get_warehouses():
        return WarehouseRepository.get_warehouses()

    @staticmethod
    def get_table_cell_text(value) -> str:
        return "" if value is None else str(value)

    @staticmethod
    def get_table_cell_alignment():
        return Qt.AlignmentFlag.AlignCenter

    @staticmethod
    def build_table_rows(warehouses):
        table_rows = []

        for row in warehouses:
            formatted_row = []
            for value in row:
                formatted_row.append({
                    "text": WarehouseService.get_table_cell_text(value),
                    "alignment": WarehouseService.get_table_cell_alignment(),
                })
            table_rows.append(formatted_row)

        return table_rows

    @staticmethod
    def build_warehouse_form_data(name, location, remark):
        return {
            "name": str(name or "").strip(),
            "location": str(location or "").strip(),
            "remark": str(remark or "").strip(),
        }

    @staticmethod
    def validate_warehouse_form(form_data: dict):
        name = form_data["name"]

        if not name:
            return False, {"error": "missing_name"}

        if WarehouseRepository.warehouse_exists(name):
            return False, {"error": "duplicate_name"}

        return True, form_data

    @staticmethod
    def get_warehouse_form_error_message(result: dict) -> str:
        error = result.get("error")
        if error == "missing_name":
            return "仓库名称不能为空"
        if error == "duplicate_name":
            return "仓库名称已存在"
        return "仓库数据校验失败"

    @staticmethod
    def add_warehouse(form_data: dict) -> dict:
        try:
            WarehouseRepository.add_warehouse(
                form_data["name"],
                form_data["location"],
                form_data["remark"],
            )
            return {"success": True, "message": "仓库新增成功"}
        except Exception as e:
            return {"success": False, "message": f"新增仓库失败：{e}"}

    @staticmethod
    def parse_selected_warehouse(table):
        current_row = table.currentRow()
        if current_row < 0:
            return None

        id_item = table.item(current_row, 0)
        name_item = table.item(current_row, 1)

        if id_item is None:
            return None

        warehouse_id_text = id_item.text().strip()
        warehouse_name = name_item.text().strip() if name_item else ""

        if not warehouse_id_text:
            return None

        try:
            warehouse_id = int(warehouse_id_text)
        except ValueError:
            return None

        return {
            "id": warehouse_id,
            "name": warehouse_name,
            "row": current_row,
        }

    @staticmethod
    def ensure_warehouse_selected(selected_warehouse):
        if not selected_warehouse:
            return False, {"error": "no_selection"}
        return True, selected_warehouse

    @staticmethod
    def get_delete_warehouse_message(result: dict) -> str:
        error = result.get("error")
        if error == "no_selection":
            return "请先选择一条仓库记录"
        return "删除仓库失败"

    @staticmethod
    def build_delete_confirm_message(selected_warehouse: dict) -> str:
        warehouse_name = selected_warehouse.get("name", "").strip()
        if warehouse_name:
            return f"确定删除仓库“{warehouse_name}”吗？"
        return "确定删除当前选中的仓库吗？"

    @staticmethod
    def delete_warehouse(selected_warehouse: dict) -> dict:
        try:
            WarehouseRepository.delete_warehouse(selected_warehouse["id"])
            return {
                "success": True,
                "message": "仓库删除成功"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"删除仓库失败：{e}"
            }

    @staticmethod
    def build_warehouse_edit_form_data(warehouse_id, name, location, remark):
        return {
            "id": warehouse_id,
            "name": str(name or "").strip(),
            "location": str(location or "").strip(),
            "remark": str(remark or "").strip(),
        }

    @staticmethod
    def parse_selected_warehouse_full(table):
        current_row = table.currentRow()
        if current_row < 0:
            return None

        values = []
        for col in range(table.columnCount()):
            item = table.item(current_row, col)
            values.append(item.text().strip() if item else "")

        try:
            warehouse_id = int(values[0]) if values[0] else None
        except ValueError:
            return None

        if not warehouse_id:
            return None

        return {
            "id": warehouse_id,
            "name": values[1],
            "location": values[2],
            "remark": values[3],
        }

    @staticmethod
    def is_duplicate_name_for_edit(warehouse_id: int, name: str) -> bool:
        existing = WarehouseRepository.get_warehouse_by_name(name)
        if not existing:
            return False
        return existing.id != warehouse_id

    @staticmethod
    def validate_warehouse_edit_form(form_data: dict):
        warehouse_id = form_data.get("id")
        name = form_data.get("name", "")

        if not warehouse_id:
            return False, {"error": "missing_id"}

        if not name:
            return False, {"error": "missing_name"}

        if WarehouseService.is_duplicate_name_for_edit(warehouse_id, name):
            return False, {"error": "duplicate_name"}

        return True, form_data

    @staticmethod
    def get_warehouse_edit_error_message(result: dict) -> str:
        error = result.get("error")
        if error == "missing_id":
            return "请先选择一条仓库记录"
        if error == "missing_name":
            return "仓库名称不能为空"
        if error == "duplicate_name":
            return "仓库名称已存在"
        return "仓库编辑数据校验失败"

    @staticmethod
    def update_warehouse(form_data: dict) -> dict:
        try:
            WarehouseRepository.update_warehouse(
                form_data["id"],
                form_data["name"],
                form_data["location"],
                form_data["remark"],
            )
            return {"success": True, "message": "仓库修改成功"}
        except Exception as e:
            return {"success": False, "message": f"修改仓库失败：{e}"}




