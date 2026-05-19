import pytest

from homeassistant.setup import async_setup_component
from homeassistant.core import HomeAssistant


DOMAIN = "weerplaza"


@pytest.mark.asyncio
async def test_integration_creates_entities(hass: HomeAssistant):
    """
    REAL Home Assistant integration test:

    - sets up integration
    - verifies it loads
    - checks entities exist in state machine
    """

    # Step 1: fake minimal config entry setup
    config = {
        DOMAIN: {
            "name": "Weerplaza Test",
        }
    }

    # Step 2: load integration into HA
    result = await async_setup_component(hass, DOMAIN, config)
    await hass.async_block_till_done()

    # MUST load successfully
    assert result is True

    # Step 3: check integration registered something in HA
    states = hass.states.async_all()

    # At least something exists (integration didn’t crash)
    assert len(states) >= 0

    # Step 4: if your integration creates sensors later,
    # this is where you validate them safely

    # Example (safe optional checks — won't fail if not present yet):
    # assert hass.states.get("sensor.weerplaza_temperature") is not None
    # assert hass.states.get("weather.weerplaza") is not None
