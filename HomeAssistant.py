import requests

HA_URL = "http://10.146.1.148:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0YTRjZWFiN2JlNzg0OWFlOTBhNTQwZmNiMzQ2NmYxZCIsImlhdCI6MTc4MzM2NjM5MiwiZXhwIjoyMDk4NzI2MzkyfQ.r4dMSFCEdVs6uiZ6csx6WZv_zyKQnxNnTkQx9oOrdKY"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def turn_on(entity):

    requests.post(
        HA_URL + "/api/services/switch/turn_on",
        headers=headers,
        json={
            "entity_id": entity
        }
    )


def turn_off(entity):

    requests.post(
        HA_URL + "/api/services/switch/turn_off",
        headers=headers,
        json={
            "entity_id": entity
        }
    )

def get_state(entity):

    response = requests.get(
        HA_URL + "/api/states/" + entity,
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        return data["state"]
    return None


def toggle(entity):
    state = get_state(entity)
    if state == "on":
        turn_off(entity)
    else:
        turn_on(entity)