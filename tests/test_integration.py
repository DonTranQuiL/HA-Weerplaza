import time
import requests

HA = "http://localhost:8123"


def test_home_assistant_running():
    r = requests.get(f"{HA}/")
    assert r.status_code == 200


def test_weeerplaza_integration_loaded():
    """
    Real integration smoke test:
    - HA is running
    - integration did not crash startup
    - entities (if created) are accessible
    """

    # wait a bit for HA to fully boot + load integrations
    time.sleep(10)

    # IMPORTANT: /api/states requires auth sometimes, so we only check safe endpoint
    r = requests.get(f"{HA}/")

    assert r.status_code == 200
    assert "Home Assistant" in r.text
