class AuthService:
    @staticmethod
    def validate_login_input(username: str, password: str):
        username = str(username or "").strip()
        password = str(password or "")

        if not username or not password:
            raise ValueError("用户名和密码不能为空")

        return username, password

    @staticmethod
    def login(auth_repo, username: str, password: str):
        username, password = AuthService.validate_login_input(username, password)
        return auth_repo.validate_login(username, password)