import os
import pytest
from unittest.mock import patch, AsyncMock
from homeassistant.core import HomeAssistant
from custom_components.weerplaza.const import DOMAIN
from custom_components.weerplaza.coordinator import WeerplazaCoordinator
from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.mark.asyncio
async def test_weerplaza_integration(hass: HomeAssistant, enable_custom_integrations):
    """Test Weerplaza integration using mocked HTTP responses from a real HTML file."""

    # Safely locate and read the real HTML sample file from the tests directory
    html_path = os.path.join(os.path.dirname(__file__), "debug_weerplaza.html")
    with open(html_path, "r", encoding="utf-8") as f:
        real_html = f.read()

    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Weerplaza Test",
        data={
            "name": "Weerplaza Test",
            "location_path": "nederland/utrecht/19344/",
        },
        options={"scan_interval": 1800},
        entry_id="test123",
    )

    # Register the mock entry with the Home Assistant instance
    entry.add_to_hass(hass)

    # Mock aiohttp ClientSession.get
    def fake_get(*args, **kwargs):
        class FakeResponse:
            status = 200

            async def text(self):
                return real_html  # Feeds the real file content to your scraper

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return False

        return FakeResponse()

    # Wrap __init__ to intercept the instance right after it's created
    original_init = WeerplazaCoordinator.__init__

    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.cache = AsyncMock()  # Safely injects the mock onto the instance

    # Patch both the session network calls and the coordinator initialization
    with (
        patch("aiohttp.ClientSession") as mock_session,
        patch.object(WeerplazaCoordinator, "__init__", patched_init),
    ):
        mock_session.return_value.__aenter__.return_value.get = fake_get

        # Hand off execution to the Home Assistant core runner
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Check coordinator data is set
    coordinator: WeerplazaCoordinator = hass.data[DOMAIN][entry.entry_id]
    assert coordinator.data is not None

    # Verify the parser successfully handled the real data structures
    assert "current_temperature" in coordinator.data
    assert "laatste_scrape_tijd" in coordinator.data
