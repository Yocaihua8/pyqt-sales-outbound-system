from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    """用户数据模型"""
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""   # 存储哈希值，不存明文
    role: str = "user"        # 'admin' 或 'user'
    created_at: Optional[datetime] = None

    def to_tuple(self):
        """转换为插入数据库所需的元组（不含id）"""
        return (self.username, self.password_hash, self.role, self.created_at)

@dataclass
class Product:
    id: Optional[int] = None
    name: str = ""
    specification: str = ""
    unit: str = ""
    unit_price: float = 0.0
    remark: str = ""

@dataclass
class Warehouse:
    id: Optional[int] = None
    name: str = ""
    location: str = ""
    remark: str = ""

@dataclass
class InboundRecord:
    id: Optional[int] = None
    product_id: int = 0
    warehouse_id: int = 0
    quantity: float = 0.0
    unit_price: float = 0.0
    total_amount: float = 0.0
    remark: str = ""
    created_at: Optional[datetime] = None

    def to_tuple(self):
        return (
            self.product_id,
            self.warehouse_id,
            self.quantity,
            self.unit_price,
            self.total_amount,
            self.remark,
            self.created_at
        )

@dataclass
class OutboundRecord:
    id: Optional[int] = None
    product_name: str = ""
    specification: str = ""
    color: str = ""
    pieces: int = 0
    quantity: float = 0.0
    unit_price: float = 0.0
    amount: float = 0.0
    remark: str = ""

    def to_tuple(self):
        return (self.product_name, self.specification, self.color, self.pieces,
                self.quantity, self.unit_price, self.amount, self.remark)

@dataclass
class OutboundStockRecord:
    id: Optional[int] = None
    product_id: int = 0
    warehouse_id: int = 0
    quantity: float = 0.0
    unit_price: float = 0.0
    total_amount: float = 0.0
    remark: str = ""
    created_at: Optional[datetime] = None

    def to_tuple(self):
        return (
            self.product_id,
            self.warehouse_id,
            self.quantity,
            self.unit_price,
            self.total_amount,
            self.remark,
            self.created_at
        )

@dataclass
class StockSummary:
    product_name: str = ""
    warehouse_name: str = ""
    inbound_qty: float = 0.0
    outbound_qty: float = 0.0
    stock_qty: float = 0.0

class SalesOutboundOrder:
    def __init__(
        self,
        id=None,
        order_no="",
        order_date="",
        warehouse_name="",

        customer_id=None,
        customer_name="",
        customer_phone="",
        customer_address="",
        customer_contact="",

        summary_remark="",
        total_amount=0.0,
        amount_in_words="",

        company_id=None,
        company_name="",
        company_phone="",
        company_address="",
        company_contact="",

        handler="",
        recorder="",
        reviewer="",
        sign_remark="",
        created_at=None
    ):
        self.id = id
        self.order_no = order_no
        self.order_date = order_date
        self.warehouse_name = warehouse_name

        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_phone = customer_phone
        self.customer_address = customer_address
        self.customer_contact = customer_contact

        self.summary_remark = summary_remark
        self.total_amount = total_amount
        self.amount_in_words = amount_in_words

        self.company_id = company_id
        self.company_name = company_name
        self.company_phone = company_phone
        self.company_address = company_address
        self.company_contact = company_contact

        self.handler = handler
        self.recorder = recorder
        self.reviewer = reviewer
        self.sign_remark = sign_remark
        self.created_at = created_at

class SalesOutboundItem:
    def __init__(
        self,
        id=None,
        order_id=None,
        line_no=0,
        product_name="",
        specification="",
        color="",
        pieces=0,
        quantity=0.0,
        unit_price=0.0,
        amount=0.0,
        remark=""
    ):
        self.id = id
        self.order_id = order_id
        self.line_no = line_no
        self.product_name = product_name
        self.specification = specification
        self.color = color
        self.pieces = pieces
        self.quantity = quantity
        self.unit_price = unit_price
        self.amount = amount
        self.remark = remark

@dataclass
class CompanyArchive:
    id: Optional[int] = None
    company_name: str = ""
    company_phone: str = ""
    company_address: str = ""
    company_contact: str = ""
    is_active: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class CustomerArchive:
    id: Optional[int] = None
    customer_name: str = ""
    customer_phone: str = ""
    customer_address: str = ""
    customer_contact: str = ""
    remark: str = ""
    is_active: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class AppSetting:
    key: str = ""
    value: str = ""