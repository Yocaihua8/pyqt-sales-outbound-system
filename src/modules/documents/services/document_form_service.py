from PyQt6.QtWidgets import QLineEdit


class DocumentFormService:
    @staticmethod
    def get_widget_value(widget):
        if isinstance(widget, QLineEdit):
            return widget.text().strip()
        return ""

    @staticmethod
    def set_widget_value(widget, value):
        if isinstance(widget, QLineEdit):
            widget.setText("" if value is None else str(value))

    @staticmethod
    def collect_form_data(field_defs: list, widget_map: dict):
        data = {}

        for field in field_defs:
            key = field["key"]
            widget = widget_map.get(key)
            if widget is not None:
                data[key] = DocumentFormService.get_widget_value(widget)

        return data

    @staticmethod
    def clear_widgets(widget_map: dict, exclude_keys: set | None = None):
        exclude_keys = exclude_keys or set()

        for key, widget in widget_map.items():
            if key in exclude_keys:
                continue

            if isinstance(widget, QLineEdit):
                widget.clear()

    @staticmethod
    def apply_form_data(widget_map: dict, form_data: dict, exclude_keys: set | None = None):
        exclude_keys = exclude_keys or set()

        for key, widget in widget_map.items():
            if key in exclude_keys:
                continue

            DocumentFormService.set_widget_value(widget, form_data.get(key, ""))

    @staticmethod
    def clear_multiple_widget_maps(widget_maps: list[dict], exclude_keys: set | None = None):
        for widget_map in widget_maps:
            DocumentFormService.clear_widgets(widget_map, exclude_keys)

    @staticmethod
    def apply_multiple_form_maps(widget_maps: list[dict], form_data: dict, exclude_keys: set | None = None):
        for widget_map in widget_maps:
            DocumentFormService.apply_form_data(widget_map, form_data, exclude_keys)