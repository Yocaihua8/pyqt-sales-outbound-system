from datetime import datetime
from typing import Dict, List, Tuple
from PyQt6.QtCore import Qt

from src.config.sales_outbound_fields import HEADER_FIELDS, FOOTER_FIELDS

from src.core.models import SalesOutboundOrder, SalesOutboundItem
from src.modules.sales.repositories.sales_outbound_repository import SalesOutboundRepository


DEFAULT_DETAIL_ROW_COUNT = 7

class SalesOutboundService:
    @staticmethod
    def generate_order_no() -> str:
        return "XS" + datetime.now().strftime("%Y%m%d%H%M%S")

    @staticmethod
    def validate_required_fields(header_data: Dict[str, str], required_fields: List[Dict]) -> Tuple[bool, List[str]]:
        missing_labels = []

        for field in required_fields:
            if field.get("required"):
                key = field["key"]
                value = str(header_data.get(key, "") or "").strip()
                if not value:
                    missing_labels.append(field["label"])

        return len(missing_labels) == 0, missing_labels

    @staticmethod
    def normalize_order_data(header_data: Dict[str, str], footer_data: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, str]]:
        header_data = dict(header_data)
        footer_data = dict(footer_data)

        order_no = str(header_data.get("order_no", "") or "").strip()
        if not order_no:
            order_no = SalesOutboundService.generate_order_no()
            header_data["order_no"] = order_no

        order_date = str(header_data.get("order_date", "") or "").strip()
        if not order_date:
            order_date = datetime.now().strftime("%Y-%m-%d")
            header_data["order_date"] = order_date

        total_amount_text = str(footer_data.get("total_amount", "") or "").strip()
        try:
            total_amount = float(total_amount_text) if total_amount_text else 0.0
        except ValueError:
            total_amount = 0.0

        footer_data["total_amount"] = f"{total_amount:.2f}"
        return header_data, footer_data

    @staticmethod
    def build_order(header_data: Dict[str, str], footer_data: Dict[str, str]) -> SalesOutboundOrder:
        total_amount_text = str(footer_data.get("total_amount", "") or "").strip()
        try:
            total_amount = float(total_amount_text) if total_amount_text else 0.0
        except ValueError:
            total_amount = 0.0

        return SalesOutboundOrder(
            order_no=header_data.get("order_no", ""),
            order_date=header_data.get("order_date", ""),
            warehouse_name=header_data.get("warehouse_name", ""),

            customer_id=header_data.get("customer_id"),
            customer_name=header_data.get("customer_name", ""),
            customer_phone=header_data.get("customer_phone", ""),
            customer_address=header_data.get("customer_address", ""),
            customer_contact=header_data.get("customer_contact", ""),

            summary_remark=header_data.get("summary_remark", ""),
            total_amount=total_amount,
            amount_in_words=footer_data.get("amount_in_words", ""),

            company_id=footer_data.get("company_id"),
            company_name=footer_data.get("company_name", ""),
            company_phone=footer_data.get("company_phone", ""),
            company_address=footer_data.get("company_address", ""),
            company_contact=footer_data.get("company_contact", ""),

            handler=footer_data.get("handler", ""),
            recorder=footer_data.get("recorder", ""),
            reviewer=footer_data.get("reviewer", ""),
            sign_remark=footer_data.get("sign_remark", ""),
            created_at=datetime.now()
        )

    @staticmethod
    def save_order(header_data: Dict[str, str], footer_data: Dict[str, str], items: List[SalesOutboundItem]) -> int:
        order = SalesOutboundService.build_order(header_data, footer_data)
        return SalesOutboundRepository.save_order_document(order, items)

    @staticmethod
    def prepare_order_for_save(header_data, footer_data, items):
        is_valid, missing_labels = SalesOutboundService.validate_required_fields(
            header_data,
            HEADER_FIELDS
        )
        if not is_valid:
            return False, {
                "error": "missing_required_fields",
                "missing_labels": missing_labels,
            }

        header_data, footer_data = SalesOutboundService.normalize_order_data(
            header_data,
            footer_data
        )

        if not items:
            return False, {
                "error": "empty_items"
            }

        return True, {
            "header_data": header_data,
            "footer_data": footer_data,
            "items": items,
        }

    @staticmethod
    def get_order_with_items(order_id: int):
        return SalesOutboundRepository.get_order_with_items(order_id)

    @staticmethod
    def query_orders(order_no="", customer_name="", start_date="", end_date=""):
        if start_date and end_date and start_date > end_date:
            raise ValueError("开始日期不能大于结束日期")

        return SalesOutboundRepository.get_orders(
            order_no=order_no,
            customer_name=customer_name,
            start_date=start_date,
            end_date=end_date
        )

    @staticmethod
    def validate_query_conditions(start_date="", end_date=""):
        if start_date and end_date and start_date > end_date:
            raise ValueError("开始日期不能大于结束日期")

    @staticmethod
    def format_query_row(row_data):
        formatted_row = []

        for col_index, value in enumerate(row_data):
            if value is None:
                text = ""
            elif col_index == 5:
                try:
                    text = f"{float(value):.2f}"
                except (ValueError, TypeError):
                    text = ""
            else:
                text = str(value)

            formatted_row.append(text)

        return formatted_row

    @staticmethod
    def build_query_table_rows(order_no="", customer_name="", start_date="", end_date=""):
        SalesOutboundService.validate_query_conditions(start_date, end_date)

        rows = SalesOutboundService.query_orders(
            order_no=order_no,
            customer_name=customer_name,
            start_date=start_date,
            end_date=end_date
        )

        return [SalesOutboundService.format_query_row(row) for row in rows]

    @staticmethod
    def get_query_cell_alignment(col_index):
        if col_index == 5:
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        elif col_index == 0:
            return Qt.AlignmentFlag.AlignCenter
        else:
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

    @staticmethod
    def parse_selected_order_id(table, id_column=0):
        current_row = table.currentRow()
        if current_row < 0:
            return None

        item = table.item(current_row, id_column)
        if item is None:
            return None

        text = item.text().strip()
        if not text:
            return None

        try:
            return int(text)
        except ValueError:
            return None

    @staticmethod
    def parse_selected_order_no(table, order_no_column=1):
        current_row = table.currentRow()
        if current_row < 0:
            return None

        item = table.item(current_row, order_no_column)
        if item is None:
            return None

        text = item.text().strip()
        return text or None

    @staticmethod
    def ensure_order_selected(order_id):
        if not order_id:
            raise ValueError("请先选择一条单据")
        return order_id

    @staticmethod
    def ensure_text_selected(value, message="请先选择一条单据"):
        text = str(value or "").strip()
        if not text:
            raise ValueError(message)
        return text

    @staticmethod
    def build_document_data(title: str, header_data: dict, footer_data: dict, items: list):
        return {
            "title": title,

            "header": header_data,
            "footer": footer_data,

            # 兼容旧打印逻辑
            "warehouse": header_data.get("warehouse_name", ""),
            "order_no": header_data.get("order_no", ""),
            "order_date": header_data.get("order_date", ""),
            "customer_name": header_data.get("customer_name", ""),
            "customer_phone": header_data.get("customer_phone", ""),
            "customer_address": header_data.get("customer_address", ""),
            "customer_contact": header_data.get("customer_contact", ""),
            "summary": header_data.get("summary_remark", ""),

            "total_amount": footer_data.get("total_amount", ""),
            "amount_in_words": footer_data.get("amount_in_words", ""),
            "company_name": footer_data.get("company_name", ""),
            "company_phone": footer_data.get("company_phone", ""),
            "company_address": footer_data.get("company_address", ""),
            "company_contact": footer_data.get("company_contact", ""),
            "handler": footer_data.get("handler", ""),
            "recorder": footer_data.get("recorder", ""),
            "reviewer": footer_data.get("reviewer", ""),
            "sign_remark": footer_data.get("sign_remark", ""),

            "items": items
        }

    @staticmethod
    def collect_form_data(field_defs: list, widget_map: dict, getter):
        data = {}
        for field in field_defs:
            key = field["key"]
            widget = widget_map.get(key)
            if widget is not None:
                data[key] = getter(widget)
        return data

    @staticmethod
    def collect_header_data(field_defs: list, widget_map: dict, getter):
        return SalesOutboundService.collect_form_data(field_defs, widget_map, getter)

    @staticmethod
    def collect_footer_data(field_defs: list, widget_map: dict, getter):
        return SalesOutboundService.collect_form_data(field_defs, widget_map, getter)

    @staticmethod
    def parse_int(value) -> int:
        text = str(value or "").strip()
        try:
            return int(text) if text else 0
        except ValueError:
            return 0

    @staticmethod
    def parse_float(value) -> float:
        text = str(value or "").strip()
        try:
            return float(text) if text else 0.0
        except ValueError:
            return 0.0

    @staticmethod
    def calculate_amount(quantity_text, unit_price_text) -> float:
        quantity = SalesOutboundService.parse_float(quantity_text)
        unit_price = SalesOutboundService.parse_float(unit_price_text)
        return quantity * unit_price

    @staticmethod
    def format_amount(amount: float) -> str:
        return f"{float(amount):.2f}"

    @staticmethod
    def calculate_row_amount_from_table(table, row: int) -> float:
        quantity_text = SalesOutboundService.get_table_item_text(table, row, 5)
        unit_price_text = SalesOutboundService.get_table_item_text(table, row, 6)
        return SalesOutboundService.calculate_amount(quantity_text, unit_price_text)

    @staticmethod
    def calculate_total_amount_from_table(table) -> float:
        total = 0.0

        for row in range(table.rowCount()):
            amount_text = SalesOutboundService.get_table_item_text(table, row, 7)
            total += SalesOutboundService.parse_float(amount_text)

        return total

    @staticmethod
    def build_total_amount_patch(total: float) -> dict:
        return {
            "total_amount": SalesOutboundService.format_amount(total),
            "amount_in_words": SalesOutboundService.number_to_chinese_upper(total),
        }

    @staticmethod
    def build_item_from_row(row_index: int, row_data: dict) -> SalesOutboundItem | None:
        product_name = str(row_data.get("product_name", "") or "").strip()
        specification = str(row_data.get("specification", "") or "").strip()
        color = str(row_data.get("color", "") or "").strip()
        pieces_text = row_data.get("pieces", "")
        quantity_text = row_data.get("quantity", "")
        unit_price_text = row_data.get("unit_price", "")
        amount_text = row_data.get("amount", "")
        remark = str(row_data.get("remark", "") or "").strip()

        # 空行直接跳过
        if not product_name and not specification and not str(quantity_text).strip() and not str(unit_price_text).strip():
            return None

        pieces = SalesOutboundService.parse_int(pieces_text)
        quantity = SalesOutboundService.parse_float(quantity_text)
        unit_price = SalesOutboundService.parse_float(unit_price_text)

        amount_str = str(amount_text or "").strip()
        if amount_str:
            amount = SalesOutboundService.parse_float(amount_str)
        else:
            amount = quantity * unit_price

        return SalesOutboundItem(
            line_no=row_index + 1,
            product_name=product_name,
            specification=specification,
            color=color,
            pieces=pieces,
            quantity=quantity,
            unit_price=unit_price,
            amount=amount,
            remark=remark
        )

    @staticmethod
    def build_order_form_data(order: SalesOutboundOrder) -> Dict[str, str]:
        total_amount = ""
        if order.total_amount not in (None, ""):
            try:
                total_amount = f"{float(order.total_amount):.2f}"
            except (ValueError, TypeError):
                total_amount = ""

        return {
            "warehouse_name": order.warehouse_name or "",
            "order_no": order.order_no or "",
            "order_date": order.order_date or "",
            "customer_name": order.customer_name or "",
            "customer_phone": order.customer_phone or "",
            "customer_address": order.customer_address or "",
            "customer_contact": order.customer_contact or "",
            "summary_remark": order.summary_remark or "",

            "total_amount": total_amount,
            "amount_in_words": order.amount_in_words or "",
            "company_name": order.company_name or "",
            "company_phone": order.company_phone or "",
            "company_address": order.company_address or "",
            "company_contact": order.company_contact or "",
            "handler": order.handler or "",
            "recorder": order.recorder or "",
            "reviewer": order.reviewer or "",
            "sign_remark": order.sign_remark or "",
            "customer_id": order.customer_id,
            "company_id": order.company_id,
        }

    @staticmethod
    def build_table_row_values(item: SalesOutboundItem) -> list:
        return [
            item.line_no,
            item.product_name,
            item.specification,
            item.color,
            item.pieces,
            item.quantity,
            item.unit_price,
            item.amount,
            item.remark,
        ]

    @staticmethod
    def number_to_chinese_upper(amount: float) -> str:
        digits = "零壹贰叁肆伍陆柒捌玖"
        units = ["", "拾", "佰", "仟"]
        big_units = ["", "万", "亿"]

        if amount == 0:
            return "零元整"

        integer_part = int(amount)
        decimal_part = round(amount - integer_part, 2)

        def four_digit_to_cn(num):
            result = ""
            zero_flag = False
            str_num = str(num).zfill(4)

            for i, ch in enumerate(str_num):
                digit = int(ch)
                unit_index = 3 - i

                if digit == 0:
                    zero_flag = True
                else:
                    if zero_flag and result:
                        result += "零"
                    result += digits[digit] + units[unit_index]
                    zero_flag = False

            return result.rstrip("零")

        int_str = str(integer_part)
        groups = []
        while int_str:
            groups.insert(0, int(int_str[-4:]))
            int_str = int_str[:-4]

        cn_integer = ""
        for i, group in enumerate(groups):
            group_cn = four_digit_to_cn(group)
            if group_cn:
                cn_integer += group_cn + big_units[len(groups) - 1 - i]
            else:
                if not cn_integer.endswith("零") and cn_integer:
                    cn_integer += "零"

        cn_integer = cn_integer.rstrip("零") + "元"

        jiao = int(decimal_part * 10)
        fen = int(round(decimal_part * 100)) % 10

        if jiao == 0 and fen == 0:
            return cn_integer + "整"

        cn_decimal = ""
        if jiao > 0:
            cn_decimal += digits[jiao] + "角"
        if fen > 0:
            cn_decimal += digits[fen] + "分"

        return cn_integer + cn_decimal

    @staticmethod
    def build_print_visibility_config() -> dict:
        def is_visible(fields, key):
            for field in fields:
                if field["key"] == key:
                    return field.get("visible", True)
            return True

        return {
            "show_phone": is_visible(HEADER_FIELDS, "customer_phone"),
            "show_contact": is_visible(HEADER_FIELDS, "customer_contact"),
            "show_summary": is_visible(HEADER_FIELDS, "summary_remark"),
            "show_company_phone": is_visible(FOOTER_FIELDS, "company_phone"),
            "show_company_contact": is_visible(FOOTER_FIELDS, "company_contact"),
            "show_reviewer": is_visible(FOOTER_FIELDS, "reviewer"),
            "show_sign_remark": is_visible(FOOTER_FIELDS, "sign_remark"),
        }

    @staticmethod
    def build_query_filters(order_no, customer_name, start_date, end_date):
        return {
            "order_no": str(order_no or "").strip(),
            "customer_name": str(customer_name or "").strip(),
            "start_date": str(start_date or "").strip(),
            "end_date": str(end_date or "").strip(),
        }

    @staticmethod
    def build_query_date_range(range_type: str):
        today = datetime.now().date()

        if range_type == "today":
            start_date = today
            end_date = today
        elif range_type == "this_month":
            start_date = today.replace(day=1)
            end_date = today
        elif range_type == "all":
            start_date = datetime(2000, 1, 1).date()
            end_date = today
        else:
            raise ValueError(f"不支持的日期范围类型: {range_type}")

        return {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }

    @staticmethod
    def get_table_item_text(table, row: int, col: int) -> str:
        item = table.item(row, col)
        return item.text().strip() if item else ""

    @staticmethod
    def collect_item_row_data(table, row: int) -> dict:
        return {
            "product_name": SalesOutboundService.get_table_item_text(table, row, 1),
            "specification": SalesOutboundService.get_table_item_text(table, row, 2),
            "color": SalesOutboundService.get_table_item_text(table, row, 3),
            "pieces": SalesOutboundService.get_table_item_text(table, row, 4),
            "quantity": SalesOutboundService.get_table_item_text(table, row, 5),
            "unit_price": SalesOutboundService.get_table_item_text(table, row, 6),
            "amount": SalesOutboundService.get_table_item_text(table, row, 7),
            "remark": SalesOutboundService.get_table_item_text(table, row, 8),
        }

    @staticmethod
    def collect_items_from_table(table):
        items = []

        for row in range(table.rowCount()):
            row_data = SalesOutboundService.collect_item_row_data(table, row)
            item = SalesOutboundService.build_item_from_row(row, row_data)
            if item is not None:
                items.append(item)

        return items

    @staticmethod
    def get_prepare_order_error_message(result: dict) -> str:
        error_type = result.get("error")

        if error_type == "missing_required_fields":
            missing_labels = result.get("missing_labels", [])
            return "以下必填项未填写：\n" + "\n".join(missing_labels)

        if error_type == "empty_items":
            return "请至少填写一条商品明细"

        return "单据数据校验失败"

    @staticmethod
    def build_save_result_patch(header_data: dict, footer_data: dict) -> dict:
        return {
            "order_no": header_data.get("order_no", ""),
            "order_date": header_data.get("order_date", ""),
            "total_amount": footer_data.get("total_amount", ""),
        }

    @staticmethod
    def execute_save_order(header_data: dict, footer_data: dict, items: list) -> dict:
        try:
            order_id = SalesOutboundService.save_order(header_data, footer_data, items)
            return {
                "success": True,
                "order_id": order_id,
                "message": f"销售出库单保存成功，单据ID：{order_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"保存失败：{e}"
            }


    @staticmethod
    def build_empty_detail_row(line_no: int) -> list:
        return [
            line_no,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ]

    @staticmethod
    def build_empty_detail_rows(row_count: int = DEFAULT_DETAIL_ROW_COUNT) -> list:
        return [
            SalesOutboundService.build_empty_detail_row(i + 1)
            for i in range(row_count)
        ]

    @staticmethod
    def build_detail_rows_from_items(items: list, min_rows: int = DEFAULT_DETAIL_ROW_COUNT) -> list:
        rows = []

        for index, item in enumerate(items, start=1):
            row_values = SalesOutboundService.build_table_row_values(item)
            row_values[0] = index
            rows.append(row_values)

        while len(rows) < min_rows:
            rows.append(SalesOutboundService.build_empty_detail_row(len(rows) + 1))

        return rows

    @staticmethod
    def build_clear_document_patch(current_profile: dict | None = None,
                                   current_customer_profile: dict | None = None) -> dict:
        current_profile = current_profile or {}
        current_customer_profile = current_customer_profile or {}

        return {
            "header_data": {
                "warehouse_name": "",
                "order_no": "",
                "order_date": datetime.now().strftime("%Y-%m-%d"),
                "customer_name": current_customer_profile.get("customer_name", ""),
                "customer_phone": current_customer_profile.get("customer_phone", ""),
                "customer_address": current_customer_profile.get("customer_address", ""),
                "customer_contact": current_customer_profile.get("customer_contact", ""),
                "summary_remark": "",
            },
            "footer_data": {
                "company_name": current_profile.get("company_name", ""),
                "company_phone": current_profile.get("company_phone", ""),
                "company_address": current_profile.get("company_address", ""),
                "company_contact": current_profile.get("company_contact", ""),
                "handler": "",
                "recorder": "",
                "reviewer": "",
                "sign_remark": "",
                "amount_in_words": "零元整",
                "total_amount": "0.00",
            },
            "detail_rows": SalesOutboundService.build_empty_detail_rows(),
        }

    @staticmethod
    def process_save_document(header_data: dict, footer_data: dict, items: list) -> dict:
        ok, result = SalesOutboundService.prepare_order_for_save(
            header_data=header_data,
            footer_data=footer_data,
            items=items
        )

        if not ok:
            return {
                "success": False,
                "stage": "validate",
                "message": SalesOutboundService.get_prepare_order_error_message(result),
            }

        header_data = result["header_data"]
        footer_data = result["footer_data"]
        items = result["items"]

        patch = SalesOutboundService.build_save_result_patch(header_data, footer_data)

        save_result = SalesOutboundService.execute_save_order(
            header_data,
            footer_data,
            items
        )

        if save_result.get("success"):
            return {
                "success": True,
                "message": save_result.get("message", "保存成功"),
                "patch": patch,
                "order_id": save_result.get("order_id"),
            }

        return {
            "success": False,
            "stage": "save",
            "message": save_result.get("message", "保存失败"),
            "patch": patch,
        }

    @staticmethod
    def build_page_mode_config(read_only: bool) -> dict:
        return {
            "header_read_only": read_only,
            "footer_read_only": read_only,
            "footer_force_read_only_keys": ["total_amount"],
            "show_back_to_query": read_only,
            "table_editable": not read_only,
            "enable_add_row": not read_only,
            "enable_delete_row": not read_only,
            "enable_save": not read_only,
        }

    @staticmethod
    def build_appended_detail_row(current_row_count: int) -> list:
        return SalesOutboundService.build_empty_detail_row(current_row_count + 1)















