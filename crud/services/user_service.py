from repositories import user_repository


class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def create_user(self, data):
        return self.user_repository.create_user(data)

    def get_user(self, user_id):
        return self.user_repository.find_user(user_id)

    def update_user(self, user_id, data):
        return self.user_repository.update_user(user_id, data)


if __name__ == "__main__":
    from database import get_connection
    from repositories.user_repository import UserRepository

    conn = get_connection()
    user_repository = UserRepository(conn)
    service = UserService(user_repository)  # build the repo here and pass it in
    uid = service.create_user({"name": "...", "email": "..."})
    print(service.get_user(uid))
