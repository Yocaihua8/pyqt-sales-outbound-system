class BasicInfoService:
    @staticmethod
    def get_entry_definitions():
        return [
            {
                "key": "company_info",
                "text": "公司信息",
                "type": "page",
                "target": "company_info",
            },
            {
                "key": "customer_info",
                "text": "客户资料",
                "type": "page",
                "target": "customer_info",
            },
            {
                "key": "warehouse_info",
                "text": "仓库资料",
                "type": "todo",
                "target": "warehouse_info",
            },
        ]

    @staticmethod
    def get_todo_message(target: str) -> str:
        if target == "customer_info":
            return "客户资料功能开发中..."
        if target == "warehouse_info":
            return "仓库资料功能开发中..."
        return "功能开发中..."