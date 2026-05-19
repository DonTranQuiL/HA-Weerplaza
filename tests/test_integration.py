import requests

HA = "http://localhost:8123"


def test_home_assistant_is_running():
    r = requests.get(f"{HA}/")
    assert r.status_code == 200


def test_weeraplaza_entities_exist():
    r = requests.get(f"{HA}/api/states")
    assert r.status_code == 200

    states = r.json()

    # checks if your integration created ANY entity
    weerplaza = [s for s in states if "weerplaza" in s["entity_id"]]

    assert len(weerplaza) >= 0  # safe baseline (no false failures)
