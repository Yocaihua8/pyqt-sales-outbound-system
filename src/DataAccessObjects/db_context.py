from src.DataAccessObjects.db_connections import DatabaseConnection
from src.DataAccessObjects.db_dao import (
    OutboundDAO, UserDAO, WarehouseDAO, ProductDAO, InboundDAO, OutboundStockDAO,
    SalesOutboundOrderDAO, SalesOutboundItemDAO, CompanyDAO, CustomerDAO, AppSettingDAO,
)


# shared singleton context (kept for backward compatibility)
db_conn = DatabaseConnection()
user_dao = UserDAO(db_conn)
outbound_dao = OutboundDAO(db_conn)
warehouse_dao = WarehouseDAO(db_conn)
product_dao = ProductDAO(db_conn)
inbound_dao = InboundDAO(db_conn)
outbound_stock_dao = OutboundStockDAO(db_conn)
sales_outbound_order_dao = SalesOutboundOrderDAO(db_conn)
sales_outbound_item_dao = SalesOutboundItemDAO(db_conn)
company_dao = CompanyDAO(db_conn)
customer_dao = CustomerDAO(db_conn)
app_setting_dao = AppSettingDAO(db_conn)
