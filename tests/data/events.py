import json
from pathlib import Path


def read_event(json_path: str):
    with open(json_path) as json_file:
        data = json.loads(json_file.read())

    return data


base_path = Path(__file__).parent.parent / "events"


EVENT_GET_USER_BY_ID = read_event(base_path / "event_get_user_by_id.json")
EVENT_GET_USERS_QUERY = read_event(base_path / "event_get_users_query.json")
