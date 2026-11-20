class EventService:
    def __init__(self, event_repository):
        self.event_repository = event_repository

    def create_event(self, data):
        return self.event_repository.create_event(data)

    def get_user_events(self, user_id):
        return self.event_repository.find_user_events(user_id)

    def delete_event(self, event_id):
        return self.event_repository.delete_event(event_id)
