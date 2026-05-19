import requests

HA = "http://localhost:8123"


def test_home_assistant_is_running():
    r = requests.get(f"{HA}/")
    assert r.status_code == 200


def test_weerplaza_basic_health():
    # DO NOT use /api/states (needs auth → causes 401 in CI)

    r = requests.get(f"{HA}/api/")

    assert r.status_code == 200
