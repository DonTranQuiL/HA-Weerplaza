import json
import requests

HA_URL = "http://localhost:8123"

def test_weeraplaza_entities_exist():
    r = requests.get(f"{HA_URL}/api/states")
    assert r.status_code == 200

    states = r.json()

    weerplaza_entities = [
        s for s in states
        if "weerplaza" in s["entity_id"]
    ]

    assert len(weerplaza_entities) > 0
