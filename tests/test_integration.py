import pytest
from unittest.mock import patch, AsyncMock
from homeassistant.core import HomeAssistant
from custom_components.weerplaza.const import DOMAIN
from custom_components.weerplaza.coordinator import WeerplazaCoordinator
from pytest_homeassistant_custom_component.common import MockConfigEntry

# Load the real debug HTML if you have it
with open("tests/debug_weerplaza.html", "r", encoding="utf-8") as f:
    MOCK_HTML = f.read()


@pytest.mark.asyncio
async def test_weerplaza_integration_real_html(
    hass: HomeAssistant, enable_custom_integrations
):
    """Test Weerplaza integration using real debug HTML."""

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
    entry.add_to_hass(hass)

    # Mock aiohttp ClientSession.get
    def fake_get(*args, **kwargs):
        class FakeResponse:
            status = 200

            async def text(self):
                return MOCK_HTML

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return False

        return FakeResponse()

    original_init = WeerplazaCoordinator.__init__

    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.cache = AsyncMock()

    with (
        patch("aiohttp.ClientSession") as mock_session,
        patch.object(WeerplazaCoordinator, "__init__", patched_init),
    ):
        mock_session.return_value.__aenter__.return_value.get = fake_get
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    coordinator: WeerplazaCoordinator = hass.data[DOMAIN][entry.entry_id]

    # ✅ Test that data exists
    assert coordinator.data is not None

    # ✅ Test specific values (adjust keys to match your parser output)
    assert "temperature" in coordinator.data
    assert "humidity" in coordinator.data

    # Example: check temperature format (like "20°C")
    temp = coordinator.data["temperature"]
    hum = coordinator.data["humidity"]
    assert isinstance(temp, str) and "°" in temp
    assert isinstance(hum, str) and "%" in hum
