import pytest
from unittest.mock import patch, AsyncMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntryState
from custom_components.weerplaza.const import DOMAIN
from custom_components.weerplaza import async_setup_entry
from custom_components.weerplaza.coordinator import WeerplazaCoordinator

# Sample HTML mock (simplified)
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
        """Simulate user config entry."""
        entry_id = "test123"
        domain = DOMAIN
        title = "Weerplaza Test"
        data = {
            "name": "Weerplaza Test",
            "location_path": "nederland/utrecht/19344/",
        }
        options = {"scan_interval": 1800}
        state = ConfigEntryState.LOADED

        async def add_update_listener(self, *args, **kwargs):
            return lambda: None

    entry = FakeEntry()

    # Patch aiohttp session.get to return MOCK_HTML
    async def fake_get(*args, **kwargs):
        class FakeResponse:
            status = 200
            async def text(self):
                return MOCK_HTML
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return False
        return FakeResponse()

    # Patch ClientSession to use fake_get
    with patch("aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value.get = fake_get

        # Patch cache to avoid file I/O
        with patch.object(WeerplazaCoordinator, "cache", new_callable=AsyncMock):
            # Run the setup
            result = await async_setup_entry(hass, entry)

    assert result is True

    # Check coordinator data
    coordinator: WeerplazaCoordinator = hass.data[DOMAIN][entry.entry_id]
    assert coordinator.data is not None
    assert coordinator.data.get("laatste_scrape_tijd") is not None
