import pytest
from unittest.mock import AsyncMock, patch, MagicMock, mock_open
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.weerplaza.const import DOMAIN
from custom_components.weerplaza.coordinator import WeerplazaCoordinator

RAW_MOCK_HTML = """
<html>
<body>
    <div class="location-widget-main">
        <h2>Het weer nu in Eygelshoven</h2>
        <span class="temp">18&deg;</span>
        <div class="wx" title="Onbewolkt" style="background-image: url('https://cdn.weerplaza.nl/icon.png');"></div>
    </div>
</body>
</html>
"""

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom components during testing."""
    yield

@pytest.fixture
def mock_entry():
    return MockConfigEntry(
        domain=DOMAIN,
        data={"instance_name": "Eygelshoven", "location_path": "nederland/eygelshoven/9314"},
        options={"scan_interval": 300}
    )


@pytest.mark.asyncio
@patch("custom_components.weerplaza.coordinator.aiohttp.ClientSession")
async def test_coordinator_successful_scrape(mock_session_cls, hass: HomeAssistant, mock_entry):
    """Test full online retrieval processing loops end to end successfully."""
    mock_cache = AsyncMock()
    coord = WeerplazaCoordinator(hass, mock_entry, cache=mock_cache)

    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.text.return_value = RAW_MOCK_HTML

    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_resp
    mock_session_cls.return_value.__aenter__.return_value = mock_session

    with patch("builtins.open", mock_open()), patch("custom_components.weerplaza.coordinator.asyncio.sleep"):
        result = await coord._async_update_data()

    assert result["current_temperature"] == 18.0
    assert result["current_weather"]["description_icon_title"] == "Onbewolkt"
    mock_cache.save_assert_called_once


@pytest.mark.asyncio
@patch("custom_components.weerplaza.coordinator.aiohttp.ClientSession")
async def test_coordinator_server_error_fallback(mock_session_cls, hass: HomeAssistant, mock_entry):
    """Verify fallback systems use previous records safely when connection drops occur."""
    coord = WeerplazaCoordinator(hass, mock_entry)
    coord._last_data = {"current_temperature": 15.5}

    mock_resp = MagicMock()
    mock_resp.status = 404
    mock_session = MagicMock()
    mock_session.get.return_value.__aenter__.return_value = mock_resp
    mock_session_cls.return_value.__aenter__.return_value = mock_session

    with patch("custom_components.weerplaza.coordinator.asyncio.sleep"):
        result = await coord._async_update_data()
        
    assert result == {"current_temperature": 15.5}


@pytest.mark.asyncio
@patch("custom_components.weerplaza.coordinator.aiohttp.ClientSession")
async def test_coordinator_total_failure(mock_session_cls, hass: HomeAssistant, mock_entry):
    """Verify coordinator throws an UpdateFailed exception if no old records exist during an error."""
    coord = WeerplazaCoordinator(hass, mock_entry)
    coord._last_data = None

    mock_session_cls.side_effect = Exception("Connection Failed")

    with patch("custom_components.weerplaza.coordinator.asyncio.sleep"), pytest.raises(UpdateFailed):
        await coord._async_update_data()


def test_debug_writer_exception(hass: HomeAssistant, mock_entry):
    """Verify file writing anomalies don't compromise system stability."""
    coord = WeerplazaCoordinator(hass, mock_entry)
    with patch("builtins.open", side_effect=PermissionError):
        # Should catch gracefully internally without throwing exception
        coord._save_debug_output("test")
