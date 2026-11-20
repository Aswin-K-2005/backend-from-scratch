from crud_base import CrudBase


class EventRepository(CrudBase):
    def __init__(self, conn):
        super().__init__(conn, "events")

    def create_event(self, data):
        return self.insert(data)

    def find_user_events(self, user_id):
        row = self.find(where={"user_id": user_id})
        return row

    def delete_event(self, event_id):
        return self.delete(where={"id": event_id})


if __name__ == "__main__":
    import time
    from database import get_connection
    from repositories.user_repository import UserRepository

    conn = get_connection()
    uid = UserRepository(conn).create_user({"name": "Ev", "email": "ev@x.com"})
    events = EventRepository(conn)
    eid = events.create_event(
        {"user_id": uid, "type": "login", "details": "{}", "created_at": time.time()}
    )
    print(events.find_user_events(uid))  # [ {the login event} ]
    print(events.delete_event(eid))  # 1
    print(events.find_user_events(uid))  # []
