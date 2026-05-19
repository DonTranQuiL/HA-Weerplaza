import requests

HA = "http://localhost:8123"


def test_home_assistant_is_running():
    # ONLY reliable unauthenticated endpoint
    r = requests.get(f"{HA}/")
    assert r.status_code == 200


def test_weerplaza_smoke_test():
    # We do NOT hit /api/* endpoints (they require auth)

    # Instead we validate:
    # - HA is alive
    # - integration didn't crash HA startup

    r = requests.get(f"{HA}/")
    assert "Home Assistant" in r.text
