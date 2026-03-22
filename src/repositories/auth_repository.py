class AuthRepository:
    def __init__(self, user_dao):
        self.user_dao = user_dao

    def validate_login(self, username: str, password: str):
        return self.user_dao.validate_login(username, password)