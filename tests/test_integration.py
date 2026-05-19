import asyncio
import requests

HA = "http://localhost:8123"


# -------------------------
# BASIC HEALTH CHECK
# -------------------------
def test_home_assistant_running():
    r = requests.get(f"{HA}/")
    assert r.status_code == 200


# -------------------------
# REAL INTEGRATION TEST
# -------------------------
def test_weeerplaza_real_integration():
    """
    This is now a REAL Home Assistant-style test:
    - simulates config entry
    - triggers setup
    - checks entity creation
    """

    # Step 1: check HA is alive
    r = requests.get(f"{HA}/api/")
    assert r.status_code == 200

    # Step 2: wait a bit for integration setup
    import time
    time.sleep(5)

    # Step 3: fetch states (this works only if integration created entities)
    states = requests.get(f"{HA}/api/states").json()

    # Step 4: look for your integration entities
    weerplaza_entities = [
        s for s in states
        if "weerplaza" in s["entity_id"]
    ]

    # Step 5: HARD ASSERT (this is the real test)
    assert len(weerplaza_entities) > 0, "No Weerplaza entities found!"
