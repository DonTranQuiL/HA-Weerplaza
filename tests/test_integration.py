import pytest
from unittest.mock import AsyncMock

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntryState

from custom_components.weerplaza import async_setup_entry, DOMAIN


@pytest.mark.asyncio
async def test_weerplaza_integration_loads(hass: HomeAssistant):
    """
    Real integration test:
    - calls async_setup_entry
    - ensures coordinator is created
    """

    # --- REALISTIC config entry (NO mocking ConfigEntry class) ---
    class FakeEntry:
        entry_id = "test123"
        domain = DOMAIN
        title = "Weerplaza Test"
        data = {
            "name": "Weerplaza Test",
            "location_path": "netherlands/utrecht",  # <-- required for scraping
        }
        options = {}  # <-- fix: scan_interval or other options can be added here
        state = ConfigEntryState.LOADED

        async def add_update_listener(self, *args, **kwargs):
            return lambda: None

    entry = FakeEntry()

    # Mock HA internals that are not needed in test
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    # --- RUN SETUP ENTRY ---
    result = await async_setup_entry(hass, entry)

    # MUST succeed
    assert result is True

    # coordinator must exist
    assert DOMAIN in hass.data
    assert entry.entry_id in hass.data[DOMAIN]
