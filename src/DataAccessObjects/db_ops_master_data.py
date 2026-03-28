from .db_context import company_dao, customer_dao, app_setting_dao


def add_company(company_name: str, company_phone: str = "", company_address: str = "", company_contact: str = ""):
    return company_dao.insert(
        company_name.strip(),
        company_phone.strip(),
        company_address.strip(),
        company_contact.strip()
    )

def update_company(company_id: int, company_name: str, company_phone: str = "", company_address: str = "", company_contact: str = ""):
    company_dao.update(
        company_id,
        company_name.strip(),
        company_phone.strip(),
        company_address.strip(),
        company_contact.strip()
    )

def delete_company(company_id: int):
    company_dao.delete(company_id)

def get_all_companies():
    return company_dao.get_all()

def get_company_by_id(company_id: int):
    return company_dao.get_by_id(company_id)

def get_app_setting(key: str):
    return app_setting_dao.get_value(key)

def set_app_setting(key: str, value: str):
    app_setting_dao.set_value(key, value)

def add_customer(customer_name: str, customer_phone: str = "", customer_address: str = "",
                 customer_contact: str = "", remark: str = ""):
    return customer_dao.insert(
        customer_name.strip(),
        customer_phone.strip(),
        customer_address.strip(),
        customer_contact.strip(),
        remark.strip()
    )

def update_customer(customer_id: int, customer_name: str, customer_phone: str = "", customer_address: str = "",
                    customer_contact: str = "", remark: str = ""):
    customer_dao.update(
        customer_id,
        customer_name.strip(),
        customer_phone.strip(),
        customer_address.strip(),
        customer_contact.strip(),
        remark.strip()
    )

def delete_customer(customer_id: int):
    customer_dao.delete(customer_id)

def get_all_customers():
    return customer_dao.get_all()

def get_customer_by_id(customer_id: int):
    return customer_dao.get_by_id(customer_id)

