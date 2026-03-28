import os
import json
from typing import Dict


class CompanyProfileService:
    DEFAULT_PROFILE = {
        "company_name": "",
        "company_phone": "",
        "company_address": "",
        "company_contact": "",
    }

    @classmethod
    def load_legacy_profile(cls) -> Dict[str, str]:
        return cls.load()

    @classmethod
    def has_legacy_profile(cls) -> bool:
        file_path = cls.get_profile_path()
        return os.path.exists(file_path)

    @staticmethod
    def get_profile_path() -> str:
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..")
        )
        config_dir = os.path.join(project_root, "config")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "company_profile.json")

    @classmethod
    def get_default_profile(cls) -> Dict[str, str]:
        return cls.DEFAULT_PROFILE.copy()

    @classmethod
    def normalize_profile(cls, data: Dict[str, str] | None) -> Dict[str, str]:
        data = data or {}
        return {
            "company_name": str(data.get("company_name", "") or "").strip(),
            "company_phone": str(data.get("company_phone", "") or "").strip(),
            "company_address": str(data.get("company_address", "") or "").strip(),
            "company_contact": str(data.get("company_contact", "") or "").strip(),
        }

    @classmethod
    def load(cls) -> Dict[str, str]:
        file_path = cls.get_profile_path()
        if not os.path.exists(file_path):
            return cls.get_default_profile()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.normalize_profile(data)
        except Exception:
            return cls.get_default_profile()

    @classmethod
    def save(cls, data: Dict[str, str]) -> Dict[str, str]:
        normalized = cls.normalize_profile(data)
        file_path = cls.get_profile_path()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(normalized, f, ensure_ascii=False, indent=2)

        return normalized