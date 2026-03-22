from typing import Optional, List, Dict

from src.core.models import CustomerArchive
from DataAccessObjects import db_operations


class CustomerArchiveService:
    LAST_USED_CUSTOMER_KEY = "last_used_customer_id"

    @staticmethod
    def _row_to_archive(row) -> CustomerArchive:
        return CustomerArchive(
            id=row["id"] if hasattr(row, "keys") else row[0],
            customer_name=row["customer_name"] if hasattr(row, "keys") else row[1],
            customer_phone=row["customer_phone"] if hasattr(row, "keys") else row[2],
            customer_address=row["customer_address"] if hasattr(row, "keys") else row[3],
            customer_contact=row["customer_contact"] if hasattr(row, "keys") else row[4],
            remark=row["remark"] if hasattr(row, "keys") else row[5],
            is_active=row["is_active"] if hasattr(row, "keys") else row[6],
            created_at=row["created_at"] if hasattr(row, "keys") else row[7],
            updated_at=row["updated_at"] if hasattr(row, "keys") else row[8],
        )

    @staticmethod
    def normalize_archive(data: dict | None) -> dict:
        data = data or {}
        return {
            "customer_name": str(data.get("customer_name", "") or "").strip(),
            "customer_phone": str(data.get("customer_phone", "") or "").strip(),
            "customer_address": str(data.get("customer_address", "") or "").strip(),
            "customer_contact": str(data.get("customer_contact", "") or "").strip(),
            "remark": str(data.get("remark", "") or "").strip(),
        }

    @staticmethod
    def validate_archive(data: dict) -> tuple[bool, str]:
        if not str(data.get("customer_name", "") or "").strip():
            return False, "客户名称不能为空"
        return True, ""

    @classmethod
    def list_archives(cls) -> List[CustomerArchive]:
        rows = db_operations.get_all_customers()
        return [cls._row_to_archive(row) for row in rows]

    @classmethod
    def get_archive(cls, customer_id: int) -> Optional[CustomerArchive]:
        row = db_operations.get_customer_by_id(customer_id)
        if not row:
            return None
        return cls._row_to_archive(row)

    @classmethod
    def save_archive(cls, data: dict, customer_id: int | None = None) -> tuple[bool, str, Optional[int]]:
        normalized = cls.normalize_archive(data)
        ok, message = cls.validate_archive(normalized)
        if not ok:
            return False, message, None

        if customer_id is None:
            new_id = db_operations.add_customer(
                normalized["customer_name"],
                normalized["customer_phone"],
                normalized["customer_address"],
                normalized["customer_contact"],
                normalized["remark"],
            )
            return True, "客户档案保存成功", new_id

        db_operations.update_customer(
            customer_id,
            normalized["customer_name"],
            normalized["customer_phone"],
            normalized["customer_address"],
            normalized["customer_contact"],
            normalized["remark"],
        )
        return True, "客户档案更新成功", customer_id

    @staticmethod
    def delete_archive(customer_id: int):
        db_operations.delete_customer(customer_id)

    @classmethod
    def get_archive_options(cls) -> list[tuple[str, int]]:
        archives = cls.list_archives()
        return [(item.customer_name, item.id) for item in archives if item.id is not None]

    @classmethod
    def get_last_used_customer_id(cls) -> Optional[int]:
        value = db_operations.get_app_setting(cls.LAST_USED_CUSTOMER_KEY)
        if not value:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def set_last_used_customer_id(cls, customer_id: int | None):
        value = "" if customer_id is None else str(customer_id)
        db_operations.set_app_setting(cls.LAST_USED_CUSTOMER_KEY, value)

    @classmethod
    def get_last_used_archive(cls) -> Optional[CustomerArchive]:
        customer_id = cls.get_last_used_customer_id()
        if customer_id is None:
            return None
        return cls.get_archive(customer_id)

    @classmethod
    def build_profile_dict(cls, archive: CustomerArchive | None) -> Dict[str, str]:
        if archive is None:
            return {
                "customer_name": "",
                "customer_phone": "",
                "customer_address": "",
                "customer_contact": "",
                "remark": "",
            }

        return {
            "customer_name": archive.customer_name or "",
            "customer_phone": archive.customer_phone or "",
            "customer_address": archive.customer_address or "",
            "customer_contact": archive.customer_contact or "",
            "remark": archive.remark or "",
        }