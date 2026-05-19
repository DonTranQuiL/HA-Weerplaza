import pytest
from unittest.mock import patch
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntryState
from custom_components.weerplaza.const import DOMAIN
from custom_components.weerplaza import async_setup_entry
from custom_components.weerplaza.coordinator import WeerplazaCoordinator

MOCK_HTML = """
<html>
  <body>
    <div id="temperature">20°C</div>
    <div id="humidity">50%</div>
  </body>
</html>
"""


@pytest.mark.asyncio
async def test_weerplaza_integration(hass: HomeAssistant):
    """Test Weerplaza integration using mocked HTTP responses."""

    class FakeEntry:
        entry_id = "test123"
        domain = DOMAIN
        title = "Weerplaza Test"
        data = {"name": "Weerplaza Test", "location_path": "nederland/utrecht/19344/"}
        options = {"scan_interval": 1800}
        state = ConfigEntryState.LOADED

        async def add_update_listener(self, *args, **kwargs):
            return lambda: None

    entry = FakeEntry()

    # Correct fake response for async context manager
    class FakeResponse:
        status = 200

        async def text(self):
            return MOCK_HTML

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

    class FakeSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

        def get(self, *args, **kwargs):
            # Return an object usable in `async with`
            return FakeResponse()

    # Patch ClientSession to return our fake session
    with patch("aiohttp.ClientSession", return_value=FakeSession()):
        result = await async_setup_entry(hass, entry)

    assert result is True
    coordinator: WeerplazaCoordinator = hass.data[DOMAIN][entry.entry_id]
    assert coordinator.data is not None
