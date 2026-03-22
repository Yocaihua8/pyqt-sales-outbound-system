from typing import Optional, List, Dict

from src.core.models import CompanyArchive
from DataAccessObjects import db_operations
from src.services.company_profile_service import CompanyProfileService


class CompanyArchiveService:
    LAST_USED_COMPANY_KEY = "last_used_company_id"

    @staticmethod
    def _row_to_archive(row) -> CompanyArchive:
        return CompanyArchive(
            id=row["id"] if hasattr(row, "keys") else row[0],
            company_name=row["company_name"] if hasattr(row, "keys") else row[1],
            company_phone=row["company_phone"] if hasattr(row, "keys") else row[2],
            company_address=row["company_address"] if hasattr(row, "keys") else row[3],
            company_contact=row["company_contact"] if hasattr(row, "keys") else row[4],
            is_active=row["is_active"] if hasattr(row, "keys") else row[5],
            created_at=row["created_at"] if hasattr(row, "keys") else row[6],
            updated_at=row["updated_at"] if hasattr(row, "keys") else row[7],
        )

    @staticmethod
    def normalize_archive(data: dict | None) -> dict:
        data = data or {}
        return {
            "company_name": str(data.get("company_name", "") or "").strip(),
            "company_phone": str(data.get("company_phone", "") or "").strip(),
            "company_address": str(data.get("company_address", "") or "").strip(),
            "company_contact": str(data.get("company_contact", "") or "").strip(),
        }

    @staticmethod
    def validate_archive(data: dict) -> tuple[bool, str]:
        if not str(data.get("company_name", "") or "").strip():
            return False, "公司名称不能为空"
        return True, ""

    @classmethod
    def list_archives(cls) -> List[CompanyArchive]:
        rows = db_operations.get_all_companies()
        return [cls._row_to_archive(row) for row in rows]

    @classmethod
    def get_archive(cls, company_id: int) -> Optional[CompanyArchive]:
        row = db_operations.get_company_by_id(company_id)
        if not row:
            return None
        return cls._row_to_archive(row)

    @classmethod
    def save_archive(cls, data: dict, company_id: int | None = None) -> tuple[bool, str, Optional[int]]:
        normalized = cls.normalize_archive(data)
        ok, message = cls.validate_archive(normalized)
        if not ok:
            return False, message, None

        if company_id is None:
            new_id = db_operations.add_company(
                normalized["company_name"],
                normalized["company_phone"],
                normalized["company_address"],
                normalized["company_contact"],
            )
            return True, "公司档案保存成功", new_id

        db_operations.update_company(
            company_id,
            normalized["company_name"],
            normalized["company_phone"],
            normalized["company_address"],
            normalized["company_contact"],
        )
        return True, "公司档案更新成功", company_id

    @staticmethod
    def delete_archive(company_id: int):
        db_operations.delete_company(company_id)

    @classmethod
    def get_archive_options(cls) -> list[tuple[str, int]]:
        archives = cls.list_archives()
        return [(item.company_name, item.id) for item in archives if item.id is not None]

    @classmethod
    def get_last_used_company_id(cls) -> Optional[int]:
        value = db_operations.get_app_setting(cls.LAST_USED_COMPANY_KEY)
        if not value:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @classmethod
    def set_last_used_company_id(cls, company_id: int | None):
        value = "" if company_id is None else str(company_id)
        db_operations.set_app_setting(cls.LAST_USED_COMPANY_KEY, value)

    @classmethod
    def get_last_used_archive(cls) -> Optional[CompanyArchive]:
        company_id = cls.get_last_used_company_id()
        if company_id is None:
            return None
        return cls.get_archive(company_id)

    @classmethod
    def migrate_legacy_profile_if_needed(cls) -> Optional[int]:
        archives = cls.list_archives()
        if archives:
            return archives[0].id

        if not CompanyProfileService.has_legacy_profile():
            return None

        legacy = CompanyProfileService.load_legacy_profile()
        normalized = cls.normalize_archive(legacy)

        if not normalized["company_name"]:
            return None

        success, _, company_id = cls.save_archive(normalized)
        if success and company_id is not None:
            cls.set_last_used_company_id(company_id)
            return company_id

        return None

    @classmethod
    def build_profile_dict(cls, archive: CompanyArchive | None) -> Dict[str, str]:
        if archive is None:
            return {
                "company_name": "",
                "company_phone": "",
                "company_address": "",
                "company_contact": "",
            }

        return {
            "company_name": archive.company_name or "",
            "company_phone": archive.company_phone or "",
            "company_address": archive.company_address or "",
            "company_contact": archive.company_contact or "",
        }