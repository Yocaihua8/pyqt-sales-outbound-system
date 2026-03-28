class UserRepository:
    def __init__(self, user_dao):
        self.user_dao = user_dao

    def get_all_users(self):
        return self.user_dao.get_all()

    def insert_user(self, user):
        return self.user_dao.insert(user)

    def update_user_role(self, user_id, role):
        return self.user_dao.update_role(user_id, role)

    def update_user_password(self, user_id, password_hash):
        return self.user_dao.update_password(user_id, password_hash)

    def delete_user(self, user_id):
        return self.user_dao.delete(user_id)