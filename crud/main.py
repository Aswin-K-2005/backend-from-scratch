from database import get_connection
import time
from repositories.user_repository import UserRepository
from repositories.event_repository import EventRepository
from services.user_service import UserService
from services.event_service import EventService

conn = get_connection()
user_repository = UserRepository(conn)
event_repository = EventRepository(conn)
user_service = UserService(user_repository)
event_service = EventService(event_repository)

user_id = user_service.create_user(
    {"name": "Aswin", "email": f"aswin1795{time.time()}@test.com"}
)
print("Created user ", user_id)

event_id = event_service.create_event(
    {
        "user_id": user_id,
        "type": "login",
        "details": "idk",
        "created_at": time.time(),
    }
)
print("Created event ", event_id)

print(user_service.get_user(user_id))
print(event_service.get_user_events(user_id))

updated = user_service.update_user(user_id, {"name": "AswinKumarSS"})
print("rows affected ", updated)
print(user_service.get_user(user_id))
deleted = event_service.delete_event(event_id)
print("rows affected", deleted)
print(event_service.get_user_events(user_id))
