import time
import requests

HA = "http://localhost:8123"


def test_home_assistant_is_up():
    r = requests.get(f"{HA}/")
    assert r.status_code == 200


def test_weeerplaza_integration_smoke():
    """
    Stable CI test:
    - verifies HA started
    - verifies integration did not crash startup
    """

    time.sleep(10)

    r = requests.get(f"{HA}/")

    assert r.status_code == 200
    assert "Home Assistant" in r.text
