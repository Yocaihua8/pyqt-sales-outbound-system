HEADER_FIELDS = [
    {"key": "warehouse_name", "label": "发货仓库", "required": True, "visible": True},
    {"key": "order_no", "label": "单据编号", "required": False, "visible": True},
    {"key": "order_date", "label": "录单日期", "required": False, "visible": True},
    {"key": "customer_name", "label": "购买单位", "required": True, "visible": True},
    {"key": "customer_phone", "label": "单位电话", "required": False, "visible": True},
    {"key": "customer_address", "label": "单位地址", "required": False, "visible": True},
    {"key": "customer_contact", "label": "联系人", "required": False, "visible": True},
    {"key": "summary_remark", "label": "备注摘要", "required": False, "visible": True},
]

FOOTER_FIELDS = [
    {"key": "total_amount", "label": "金额合计", "required": False, "visible": True},
    {"key": "amount_in_words", "label": "大写金额", "required": False, "visible": True},
    {"key": "company_name", "label": "公司名称", "required": False, "visible": True},
    {"key": "company_phone", "label": "公司电话", "required": False, "visible": True},
    {"key": "company_address", "label": "公司地址", "required": False, "visible": True},
    {"key": "company_contact", "label": "联系人", "required": False, "visible": True},
    {"key": "handler", "label": "经手人", "required": False, "visible": True},
    {"key": "recorder", "label": "录单人", "required": False, "visible": True},
    {"key": "reviewer", "label": "审核人", "required": False, "visible": True},
    {"key": "sign_remark", "label": "签字备注", "required": False, "visible": True},
]