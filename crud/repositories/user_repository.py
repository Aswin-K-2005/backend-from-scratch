from crud_base import CrudBase


class UserRepository(CrudBase):
    def __init__(self, conn):
        super().__init__(conn, "users")

    def create_user(self, data):
        return self.insert(data)

    def find_user(self, user_id):
        row = self.find(where={"id": user_id})
        if len(row) == 0:
            return None
        else:
            return row[0]

    def update_user(self, user_id, data):
        return self.update(where={"id": user_id}, data=data)
