import pytest
from unittest.mock import patch, AsyncMock

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntryState

from custom_components.weerplaza.const import DOMAIN
from custom_components.weerplaza import async_setup_entry


@pytest.mark.asyncio
async def test_weerplaza_integration_loads(hass: HomeAssistant):
    """
    Real Home Assistant integration test (correct architecture):
    - creates fake ConfigEntry
    - runs async_setup_entry
    - checks coordinator exists
    """

    # Fake config entry (this replaces async_setup_component)
    mock_entry = patch("homeassistant.config_entries.ConfigEntry", autospec=True)

    entry = mock_entry.start()
    entry.entry_id = "test123"
    entry.data = {"name": "Weerplaza Test"}
    entry.state = ConfigEntryState.LOADED

    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    result = await async_setup_entry(hass, entry)

    assert result is True
    assert DOMAIN in hass.data
    assert entry.entry_id in hass.data[DOMAIN]
