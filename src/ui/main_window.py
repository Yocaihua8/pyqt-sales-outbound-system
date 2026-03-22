from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout, QWidget, QPushButton,
    QMessageBox,
    QToolBar, QStackedWidget, QTabBar
)
from PyQt6.QtCore import Qt

from src.ui.basic_info_page import BasicInfoPage
from src.ui.sales_outbound_query_page import SalesOutboundQueryPage
from src.ui.sales_outbound_page import SalesOutboundPage
from src.ui.dashboard_page import DashboardPage
from src.ui.outbound_manager import OutboundManagerPage
from src.ui.stock_manager import StockManagerPage
from src.ui.inbound_manager import InboundManagerPage
from src.ui.product_manager import ProductManagerPage
from src.ui.warehouse_manager import WarehouseManagerPage
from src.ui.company_info_page import CompanyInfoPage
from src.ui.base_document_page import BaseDocumentPage
from src.ui.customer_info_page import CustomerInfoPage

from src.services.main_window_navigation_service import MainWindowNavigationService
from src.controllers.sales_outbound_detail_controller import SalesOutboundDetailController

from DataAccessObjects.db_operations import OutboundDAO

class MainWindow(QMainWindow):
    # ---------- 初始化与界面 ----------
    def __init__(self, dao: OutboundDAO,current_user, user_dao):
        super().__init__()
        self.dao = dao
        self.current_user = current_user
        self.user_dao = user_dao
        self.basic_info_page = BasicInfoPage(
            self,
            page_opener=self.open_basic_info_entry_page
        )
        self.company_info_page = CompanyInfoPage(self)
        self.company_info_page.profile_saved.connect(self.on_company_profile_saved)
        self.customer_info_page = CustomerInfoPage(self)
        self.customer_info_page.profile_saved.connect(self.on_customer_profile_saved)
        self.setWindowTitle("轻量级仓库管理系统 WMS v1.0")
        self.setGeometry(100, 100, 1200, 600)

        self.top_toolbar_buttons = {}
        self.module_toolbar_buttons = {}
        self.open_form_pages = {}

        self.create_ui()
        self.sales_outbound_detail_controller = SalesOutboundDetailController(
            parent_window=self,
            sales_outbound_page=self.sales_outbound_page,
            open_form_page=self.open_form_page
        )
        self._create_sales_outbound_query_page()
        self.show_dashboard_page()

    def create_ui(self):
        # ---------- 主菜单栏 ----------
        menubar = self.menuBar()

        # ---------- 文件菜单 ----------
        file_menu = menubar.addMenu('文件')

        save_action = file_menu.addAction('保存')
        save_action.triggered.connect(self.handle_save_action)

        save_as_action = file_menu.addAction('另存为...')
        save_as_action.triggered.connect(self.handle_export_pdf_action)

        file_menu.addSeparator()

        print_action = file_menu.addAction('打印...')
        print_action.triggered.connect(self.handle_print_action)

        preview_action = file_menu.addAction('打印预览')
        preview_action.triggered.connect(self.handle_print_preview_action)

        file_menu.addSeparator()

        switch_user_action = file_menu.addAction('切换用户')
        switch_user_action.triggered.connect(self.switch_user)
        file_menu.addSeparator()

        exit_action = file_menu.addAction('退出')
        exit_action.triggered.connect(self.close)

        # ---------- 管理菜单（仅管理员可见） ----------
        if self.current_user.role == 'admin':
            admin_menu = menubar.addMenu('管理')
            user_manage_action = admin_menu.addAction('用户管理')
            user_manage_action.triggered.connect(self.open_user_manager)

        # ---------- 帮助菜单 ----------
        help_menu = menubar.addMenu('帮助')
        about_action = help_menu.addAction('关于')
        about_action.triggered.connect(self.show_about_dialog)

        # ---------- 第2行：顶层栏 ----------
        self.top_toolbar = QToolBar("顶层功能")
        self.top_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.top_toolbar)

        for entry in MainWindowNavigationService.get_top_toolbar_entries():
            btn = QPushButton(entry["text"])
            btn.setCheckable(True)

            handler = getattr(self, entry["handler"])
            btn.clicked.connect(handler)

            self.top_toolbar.addWidget(btn)
            self.top_toolbar_buttons[entry["key"]] = btn

        # 顶层栏后换行，让业务功能栏单独占一行
        self.addToolBarBreak(Qt.ToolBarArea.TopToolBarArea)

        # ---------- 第3行：业务功能栏 ----------
        self.module_toolbar = QToolBar("业务功能")
        self.module_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.module_toolbar)

        self.show_sales_module_toolbar()

        # 业务功能栏后再换行，下面才是导航栏
        self.addToolBarBreak(Qt.ToolBarArea.TopToolBarArea)

        nav_toolbar = QToolBar("表单导航")
        nav_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, nav_toolbar)

        self.form_tabbar = QTabBar()
        self.form_tabbar.setTabsClosable(True)
        self.form_tabbar.setMovable(True)
        self.form_tabbar.currentChanged.connect(self.switch_form_tab)
        self.form_tabbar.tabCloseRequested.connect(self.close_form_tab)

        nav_toolbar.addWidget(self.form_tabbar)

        # ---------- 中央表格 ----------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # ---------- 创建首页页面 ----------
        self.dashboard_page = DashboardPage()

        # ---------- 库存查询页面 ----------
        self.stock_page = StockManagerPage()

        # ---------- 商品管理页面 ----------
        self.product_page = ProductManagerPage()

        # ---------- 仓库管理页面 ----------
        self.warehouse_page = WarehouseManagerPage()

        # ---------- 入库管理页面 ----------
        self.inbound_page = InboundManagerPage()

        # ---------- 出库管理页面 ----------
        self.std_outbound_page = OutboundManagerPage(self)

        self.sales_outbound_page = SalesOutboundPage(self)
        self.sales_outbound_page.back_to_query_requested.connect(
            self.show_sales_outbound_query_page
        )

        # 加入页面栈
        self.stack.addWidget(self.dashboard_page)  # index 0 首页
        self.stack.addWidget(self.stock_page)  # index 2 库存页
        self.stack.addWidget(self.product_page)  # index 3 商品页
        self.stack.addWidget(self.warehouse_page)  # index 4 仓库页
        self.stack.addWidget(self.inbound_page)  # index 5 入库页
        self.stack.addWidget(self.std_outbound_page)  # index 6 标准出库页
        self.stack.addWidget(self.sales_outbound_page)  # index 7
        self.stack.addWidget(self.basic_info_page)
        self.stack.addWidget(self.company_info_page)
        self.stack.addWidget(self.customer_info_page)

        self.stack.setCurrentWidget(self.dashboard_page)

    def _create_sales_outbound_query_page(self):
        self.sales_outbound_query_page = SalesOutboundQueryPage(
            self,
            order_detail_opener=self.open_sales_order_detail
        )
        self.stack.addWidget(self.sales_outbound_query_page)

    def get_current_page(self):
        if hasattr(self, "stack"):
            return self.stack.currentWidget()
        return None

    # ---------- 顶层导航与工具栏状态 ----------
    def get_toolbar_button_style(self, active: bool = False) -> str:
        if active:
            return """
                QPushButton {
                    background-color: #dbeafe;
                    border: 1px solid #93c5fd;
                    font-weight: bold;
                    padding: 6px 12px;
                }
            """
        return """
            QPushButton {
                padding: 6px 12px;
            }
        """

    def update_top_toolbar_selection(self, active_key: str):

        for key, btn in self.top_toolbar_buttons.items():
            is_active = (key == active_key)
            btn.setChecked(is_active)
            btn.setStyleSheet(self.get_toolbar_button_style(is_active))

    def update_module_toolbar_selection(self, active_handler_name: str | None):

        for handler_name, btn in self.module_toolbar_buttons.items():
            is_active = (handler_name == active_handler_name)
            btn.setChecked(is_active)
            btn.setStyleSheet(self.get_toolbar_button_style(is_active))

    def clear_module_toolbar(self):
        self.module_toolbar.clear()
        self.module_toolbar_buttons = {}

    def _create_module_button_handler(self, handler, handler_name):
        def wrapped_handler(checked=False):
            self.update_module_toolbar_selection(handler_name)
            handler()

        return wrapped_handler

    def render_module_toolbar(self, entries):
        self.clear_module_toolbar()

        for index, entry in enumerate(entries):
            btn = QPushButton(entry["text"])
            btn.setCheckable(True)

            handler = getattr(self, entry["handler"])
            handler_name = entry["handler"]

            btn.clicked.connect(
                self._create_module_button_handler(handler, handler_name)
            )
            self.module_toolbar.addWidget(btn)
            self.module_toolbar_buttons[handler_name] = btn

            if index == 0:
                btn.setStyleSheet(self.get_toolbar_button_style(True))
                btn.setChecked(True)
            else:
                btn.setStyleSheet(self.get_toolbar_button_style(False))

    def show_sales_module_toolbar(self):
        self.update_top_toolbar_selection("sales")
        self.render_module_toolbar(
            MainWindowNavigationService.get_sales_module_entries()
        )

    def show_stock_module_toolbar(self):
        self.update_top_toolbar_selection("stock")
        self.render_module_toolbar(
            MainWindowNavigationService.get_stock_module_entries()
        )

    def show_system_module_toolbar(self):
        self.update_top_toolbar_selection("system")
        self.render_module_toolbar(
            MainWindowNavigationService.get_system_module_entries()
        )

    def sync_navigation_state(self, top_key: str, module_handler_name: str | None = None):
        if top_key in ("home", "basic_info"):
            self.update_top_toolbar_selection(top_key)
            self.clear_module_toolbar()
            return

        if top_key == "sales":
            self.show_sales_module_toolbar()
        elif top_key == "stock":
            self.show_stock_module_toolbar()
        elif top_key == "system":
            self.show_system_module_toolbar()

        if module_handler_name:
            self.update_module_toolbar_selection(module_handler_name)

    # ---------- 页面打开与模块切换 ----------
    def show_dashboard_page(self):
        self.sync_navigation_state("home")
        self.dashboard_page.prepare_page()
        self.stack.setCurrentWidget(self.dashboard_page)

    def show_basic_info_page(self):
        self.sync_navigation_state("basic_info")
        self.open_form_page("basic_info", "基础信息", self.basic_info_page)

    def show_warehouse_page(self):
        self.sync_navigation_state("stock", "show_warehouse_page")
        self.open_form_page("warehouse", "仓库管理", self.warehouse_page)

    def show_product_page(self):
        self.sync_navigation_state("stock", "show_product_page")
        self.open_form_page("product", "商品管理", self.product_page)

    def show_inbound_page(self):
        self.sync_navigation_state("stock", "show_inbound_page")
        self.open_form_page("inbound", "入库管理", self.inbound_page)

    def show_std_outbound_page(self):
        self.sync_navigation_state("stock", "show_std_outbound_page")
        self.std_outbound_page.prepare_new_document()
        self.open_form_page("std_outbound", "标准出库", self.std_outbound_page)

    def show_stock_page(self):
        self.sync_navigation_state("stock", "show_stock_page")
        self.stock_page.prepare_page()
        self.open_form_page("stock", "库存查询", self.stock_page)

    def on_category_sales(self):
        self.sync_navigation_state("sales", "on_category_sales")
        self.sales_outbound_page.prepare_new_document()
        self.open_form_page("sales_outbound", "销售出库单", self.sales_outbound_page)

    def show_sales_outbound_query_page(self):
        self.sync_navigation_state("sales", "show_sales_outbound_query_page")
        self.sales_outbound_query_page.prepare_page()
        self.open_form_page("sales_outbound_query", "销售出库单查询", self.sales_outbound_query_page)

    def open_sales_order_detail(self, order_id: int, preview_print: bool = False):
        self.sales_outbound_detail_controller.open_detail(
            order_id,
            preview_print=preview_print
        )

    def open_company_info_page(self, target: str | None = None):
        self.sync_navigation_state("basic_info")
        self.open_form_page("company_info", "公司信息", self.company_info_page)

    def open_basic_info_entry_page(self, target: str):
        if target == "company_info":
            self.open_company_info_page(target)
            return

        if target == "customer_info":
            self.open_customer_info_page(target)
            return

        QMessageBox.information(self, "提示", f"暂未实现页面：{target}")

    def open_customer_info_page(self, target: str | None = None):
        self.sync_navigation_state("basic_info")
        self.open_form_page("customer_info", "客户资料", self.customer_info_page)

    # ---------- 表单页与导航栏 ----------
    def open_form_page(self, page_key, title, widget):
        for i in range(self.form_tabbar.count()):
            if self.form_tabbar.tabData(i) == page_key:
                self.open_form_pages[page_key] = widget
                self.form_tabbar.setCurrentIndex(i)
                self.stack.setCurrentWidget(widget)
                return

        tab_index = self.form_tabbar.addTab(title)
        self.form_tabbar.setTabData(tab_index, page_key)
        self.form_tabbar.setCurrentIndex(tab_index)
        self.open_form_pages[page_key] = widget
        self.stack.setCurrentWidget(widget)

    def switch_form_tab(self, index):
        if index < 0:
            return

        page_key = self.form_tabbar.tabData(index)
        widget = self.open_form_pages.get(page_key)
        if widget is not None:
            self.stack.setCurrentWidget(widget)

    def close_form_tab(self, index):
        if index < 0:
            return

        page_key = self.form_tabbar.tabData(index)
        self.form_tabbar.removeTab(index)

        if page_key in self.open_form_pages:
            del self.open_form_pages[page_key]

        if self.form_tabbar.count() > 0:
            self.switch_form_tab(self.form_tabbar.currentIndex())
        else:
            self.stack.setCurrentWidget(self.dashboard_page)

    # ---------- 菜单动作 ----------
    def show_action_not_supported_message(self, action_name: str):
        QMessageBox.information(self, "提示", f"当前页面暂不支持{action_name}")

    def get_active_document_page(self):
        page = self.get_current_page()
        if isinstance(page, BaseDocumentPage):
            return page
        return None

    def handle_save_action(self):
        page = self.get_active_document_page()
        if page and page.supports_save():
            page.save_document()
        else:
            self.show_action_not_supported_message("保存")

    def handle_print_preview_action(self):
        page = self.get_active_document_page()
        if page and page.supports_print():
            page.print_preview()
        else:
            self.show_action_not_supported_message("打印预览")

    def handle_print_action(self):
        page = self.get_active_document_page()
        if page and page.supports_print():
            page.print_document()
        else:
            self.show_action_not_supported_message("打印")

    def handle_export_pdf_action(self):
        page = self.get_active_document_page()
        if page and page.supports_export_pdf():
            page.export_to_pdf()
        else:
            self.show_action_not_supported_message("另存为")

    def switch_user(self):
        from main import restart_login
        self.close()
        restart_login()

    def open_user_manager(self):
        from ui.user_manager import UserManagerDialog
        dialog = UserManagerDialog(self.user_dao, self)
        dialog.exec()

    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "关于",
            "本地出库单管理系统\n版本 2.0\n\n基于 PyQt6 开发的 Excel 风格客户端。"
        )

    def closeEvent(self, event):
        # 数据库连接由 main 负责关闭
        event.accept()

    # ---------- 页面同步事件 ----------
    def on_company_profile_saved(self, profile: dict):
        self.sync_company_profile_to_pages(profile)

    def sync_company_profile_to_pages(self, profile: dict | None = None):
        if hasattr(self, "sales_outbound_page") and self.sales_outbound_page is not None:
            self.sales_outbound_page.apply_company_profile(profile)

    def on_customer_profile_saved(self, profile: dict):
        self.sync_customer_profile_to_pages(profile)

    def sync_customer_profile_to_pages(self, profile: dict | None = None):
        if hasattr(self, "sales_outbound_page") and self.sales_outbound_page is not None:
            if hasattr(self.sales_outbound_page, "apply_customer_profile"):
                self.sales_outbound_page.apply_customer_profile(profile)

    # ---------- 待分配 ----------



