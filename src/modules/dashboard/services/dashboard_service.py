class DashboardService:
    @staticmethod
    def build_dashboard_summary(summary: dict):
        summary = summary or {}

        stock_total_amount = summary.get("stock_total_amount", 0)
        try:
            stock_total_amount = f"{float(stock_total_amount):.2f}"
        except (TypeError, ValueError):
            stock_total_amount = "0.00"

        return {
            "product_count": str(summary.get("product_count", 0)),
            "warehouse_count": str(summary.get("warehouse_count", 0)),
            "inbound_count": str(summary.get("inbound_count", 0)),
            "stock_count": str(summary.get("stock_count", 0)),
            "stock_total_amount": stock_total_amount,
            "low_stock_count": str(summary.get("low_stock_count", 0)),
        }