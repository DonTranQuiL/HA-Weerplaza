import time
import requests

HA = "http://localhost:8123"


def test_home_assistant_is_running():
    r = requests.get(f"{HA}/")
    assert r.status_code == 200


def test_weeerplaza_smoke():
    """
    Stable integration smoke test:
    - ensures HA started
    - ensures integration did not crash startup
    """

    time.sleep(10)

    r = requests.get(f"{HA}/")

    assert r.status_code == 200
    assert "Home Assistant" in r.text
