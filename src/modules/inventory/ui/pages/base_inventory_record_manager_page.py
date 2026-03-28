from PyQt6.QtWidgets import QMessageBox

from src.modules.documents.ui.base_document_page import BaseDocumentPage


class BaseInventoryRecordManagerPage(BaseDocumentPage):
    def initialize_page_data(self):
        self.load_products()
        self.load_warehouses()
        self.load_data()

    def get_page_service(self):
        raise NotImplementedError

    def get_domain_service(self):
        raise NotImplementedError

    def get_repository(self):
        raise NotImplementedError

    def get_success_message(self) -> str:
        raise NotImplementedError

    def get_document_title(self) -> str:
        raise NotImplementedError

    def parse_form_data(self, form_raw: dict) -> dict:
        return self.get_domain_service().parse_form(form_raw)

    def save_record(self, form_raw: dict, form_data: dict):
        self.get_repository().add_record(form_raw, form_data)

    def before_save_record(self, form_raw: dict, form_data: dict):
        pass

    def after_save_record(self):
        pass

    def after_load_products(self):
        pass

    def after_load_warehouses(self):
        pass

    def after_load_data(self):
        pass

    def after_prepare_new_document(self):
        pass

    def load_products(self):
        page_service = self.get_page_service()
        repository = self.get_repository()
        domain_service = self.get_domain_service()

        options = page_service.build_product_options(repository, domain_service)
        page_service.apply_combo_options(self.product_box, options)
        self.after_load_products()

    def load_warehouses(self):
        page_service = self.get_page_service()
        repository = self.get_repository()
        domain_service = self.get_domain_service()

        options = page_service.build_warehouse_options(repository, domain_service)
        page_service.apply_combo_options(self.warehouse_box, options)
        self.after_load_warehouses()

    def load_data(self):
        page_service = self.get_page_service()
        domain_service = self.get_domain_service()
        repository = self.get_repository()

        rows = page_service.build_table_rows(repository, domain_service)
        page_service.populate_table(
            self.table,
            rows,
            domain_service.get_cell_alignment
        )
        self.after_load_data()

    def save_document(self):
        page_service = self.get_page_service()

        form_raw = page_service.collect_form_data(self)

        try:
            form_data = self.parse_form_data(form_raw)
            self.before_save_record(form_raw, form_data)
            self.save_record(form_raw, form_data)

            QMessageBox.information(self, "成功", self.get_success_message())

            self.prepare_new_document()
            self.load_data()
            self.after_save_record()

        except ValueError as e:
            QMessageBox.warning(self, "提示", str(e))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败：{e}")

    # ---------- 单据页通用协议实现 ----------
    def prepare_new_document(self):
        page_service = self.get_page_service()
        page_service.reset_form(self)
        self.after_prepare_new_document()

    def get_document_data(self) -> dict:
        page_service = self.get_page_service()
        return page_service.collect_form_data(self)

    def set_read_only_mode(self, read_only: bool):
        page_service = self.get_page_service()
        page_service.set_read_only_mode(self, read_only)

    def set_edit_mode(self):
        self.set_read_only_mode(False)

    def supports_save(self) -> bool:
        return True

    def supports_print(self) -> bool:
        return False

    def supports_export_pdf(self) -> bool:
        return False

    def print_preview(self):
        QMessageBox.information(self, "提示", "当前页面暂不支持打印预览")

    def print_document(self):
        QMessageBox.information(self, "提示", "当前页面暂不支持打印")

    def export_to_pdf(self):
        QMessageBox.information(self, "提示", "当前页面暂不支持导出 PDF")