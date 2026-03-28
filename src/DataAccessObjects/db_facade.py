"""
Facade layer: keeps the legacy function-style DB API.
Implementation is split by domain modules.
"""

from .db_context import (
    db_conn, user_dao, outbound_dao, warehouse_dao, product_dao, inbound_dao,
    outbound_stock_dao, sales_outbound_order_dao, sales_outbound_item_dao,
    company_dao, customer_dao, app_setting_dao,
)

from .db_ops_inventory import *
from .db_ops_sales import *
from .db_ops_master_data import *
