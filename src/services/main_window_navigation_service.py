class MainWindowNavigationService:
    @staticmethod
    def get_top_toolbar_entries():
        return [
            {"key": "home", "text": "🏠 首页", "handler": "show_dashboard_page"},
            {"key": "basic_info", "text": "🧩 基础信息", "handler": "show_basic_info_page"},
            {"key": "sales", "text": "💼 销售管理", "handler": "show_sales_module_toolbar"},
            {"key": "stock", "text": "📦 库存管理", "handler": "show_stock_module_toolbar"},
            {"key": "system", "text": "⚙️ 系统功能", "handler": "show_system_module_toolbar"},
        ]

    @staticmethod
    def get_sales_module_entries():
        return [
            {"key": "sales_outbound", "text": "💰 销售出库单", "handler": "on_category_sales"},
            {"key": "sales_outbound_query", "text": "📂 销售出库单查询", "handler": "show_sales_outbound_query_page"},
        ]

    @staticmethod
    def get_stock_module_entries():
        return [
            {"key": "inbound", "text": "📥 入库管理", "handler": "show_inbound_page"},
            {"key": "std_outbound", "text": "🚚 标准出库", "handler": "show_std_outbound_page"},
            {"key": "stock", "text": "📦 库存查询", "handler": "show_stock_page"},
            {"key": "product", "text": "📋 商品管理", "handler": "show_product_page"},
            {"key": "warehouse", "text": "🏬 仓库管理", "handler": "show_warehouse_page"},
        ]

    @staticmethod
    def get_system_module_entries():
        return [
            {"key": "user_manage", "text": "👤 用户管理", "handler": "open_user_manager"},
            {"key": "switch_user", "text": "🔄 切换用户", "handler": "switch_user"},
        ]