from src.core.models import User
from src.DataAccessObjects.db_dao_common import hash_password


class UserService:
    @staticmethod
    def build_user_table_rows(users):
        rows = []
        for user in users:
            rows.append([
                str(user.id),
                user.username,
                user.role,
                str(user.created_at)[:19] if user.created_at else ""
            ])
        return rows

    @staticmethod
    def validate_new_user(username: str, password: str):
        username = str(username or "").strip()
        password = str(password or "")

        if not username or not password:
            raise ValueError("用户名和密码不能为空")

        return username, password

    @staticmethod
    def build_new_user(username: str, password: str, role: str):
        username, password = UserService.validate_new_user(username, password)
        return User(
            username=username,
            password_hash=hash_password(password),
            role=role
        )

    @staticmethod
    def validate_new_role(current_role: str, new_role: str):
        if not new_role:
            raise ValueError("角色不能为空")
        if new_role == current_role:
            return False
        return True

    @staticmethod
    def validate_new_password(password: str):
        password = str(password or "")
        if not password:
            raise ValueError("密码不能为空")
        return hash_password(password)

    @staticmethod
    def validate_delete_user(target_username: str, current_username: str):
        if target_username == current_username:
            raise ValueError("不能删除当前登录的用户")


