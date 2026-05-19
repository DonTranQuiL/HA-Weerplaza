import pytest
from unittest.mock import AsyncMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntryState
from custom_components.weerplaza import async_setup_entry, DOMAIN


@pytest.mark.asyncio
async def test_weerplaza_integration_loads(hass: HomeAssistant):
    """
    Integration test for Weerplaza:
    - Uses a realistic config entry simulating user input from README
    - Mocks network call to prevent real HTTP requests
    - Ensures the coordinator is created and setup succeeds
    """

    # --- Simulated user config entry ---
    class FakeEntry:
        entry_id = "test123"
        domain = DOMAIN
        title = "Weerplaza Test"
        data = {
            "name": "Weerplaza Test",
            "location_path": "nederland/utrecht/19344/",  # copy from README example
        }
        options = {
            "scan_interval": 1800,  # recommended interval
        }
        state = ConfigEntryState.LOADED

        async def add_update_listener(self, *args, **kwargs):
            return lambda: None

    entry = FakeEntry()

    # --- Mock HA internals not needed in test ---
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    # --- Patch aiohttp network call to prevent real HTTP request ---
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        # Mock response object
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="<html>dummy content</html>")
        mock_get.return_value.__aenter__.return_value = mock_response

        # --- Run setup ---
        result = await async_setup_entry(hass, entry)

    # --- Assertions ---
    assert result is True, "async_setup_entry should return True"
    assert DOMAIN in hass.data, "Weerplaza domain should exist in hass.data"
    assert entry.entry_id in hass.data[DOMAIN], "Coordinator should be stored by entry_id"
