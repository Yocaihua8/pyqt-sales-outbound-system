from PyQt6.QtWidgets import QWidget


class BaseDocumentPage(QWidget):
    """
    单据页轻基类：
    只约束公共接口，不接管具体 UI。
    后续主窗口菜单/工具栏只依赖这些接口，不写死具体页面类型。
    """

    def get_document_title(self) -> str:
        raise NotImplementedError

    def get_document_data(self) -> dict:
        raise NotImplementedError

    def prepare_new_document(self):
        raise NotImplementedError

    def load_document(self, order, items):
        raise NotImplementedError

    def set_read_only_mode(self, read_only: bool):
        raise NotImplementedError

    def set_edit_mode(self):
        raise NotImplementedError

    def print_preview(self):
        raise NotImplementedError

    def print_document(self):
        raise NotImplementedError

    def export_to_pdf(self):
        raise NotImplementedError

    def save_document(self):
        raise NotImplementedError

    def supports_save(self) -> bool:
        return True

    def supports_print(self) -> bool:
        return True

    def supports_export_pdf(self) -> bool:
        return True