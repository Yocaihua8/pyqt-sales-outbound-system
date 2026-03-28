"""
DAO compatibility layer.

Concrete DAO implementations are split by domain modules:
- db_dao_common.py
- db_dao_inventory.py
- db_dao_sales.py
- db_dao_master_data.py
"""

from .db_dao_common import *
from .db_dao_inventory import *
from .db_dao_sales import *
from .db_dao_master_data import *
