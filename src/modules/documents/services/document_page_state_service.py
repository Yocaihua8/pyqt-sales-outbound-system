from PyQt6.QtWidgets import QLineEdit, QTableWidget


class DocumentPageStateService:
    @staticmethod
    def set_read_only_mode(
        *,
        header_widgets: dict,
        footer_widgets: dict,
        table: QTableWidget,
        back_to_query_btn=None,
        editable_buttons: list | None = None,
        always_read_only_keys: set | None = None,
        read_only: bool = True,
    ):
        editable_buttons = editable_buttons or []
        always_read_only_keys = always_read_only_keys or set()

        for widget in header_widgets.values():
            if isinstance(widget, QLineEdit):
                widget.setReadOnly(read_only)

        for key, widget in footer_widgets.items():
            if isinstance(widget, QLineEdit):
                if key in always_read_only_keys:
                    widget.setReadOnly(True)
                else:
                    widget.setReadOnly(read_only)

        if back_to_query_btn is not None:
            back_to_query_btn.setVisible(read_only)

        if read_only:
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        else:
            table.setEditTriggers(
                QTableWidget.EditTrigger.DoubleClicked
                | QTableWidget.EditTrigger.EditKeyPressed
                | QTableWidget.EditTrigger.AnyKeyPressed
            )

        for btn in editable_buttons:
            if btn is not None:
                btn.setEnabled(not read_only)

    @staticmethod
    def set_edit_mode(
        *,
        header_widgets: dict,
        footer_widgets: dict,
        table: QTableWidget,
        back_to_query_btn=None,
        editable_buttons: list | None = None,
        always_read_only_keys: set | None = None,
    ):
        DocumentPageStateService.set_read_only_mode(
            header_widgets=header_widgets,
            footer_widgets=footer_widgets,
            table=table,
            back_to_query_btn=back_to_query_btn,
            editable_buttons=editable_buttons,
            always_read_only_keys=always_read_only_keys,
            read_only=False,
        )