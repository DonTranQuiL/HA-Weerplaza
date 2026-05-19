import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.weerplaza.const import DOMAIN
from custom_components.weerplaza import async_setup, async_setup_entry, async_unload_entry, async_reload_entry

@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom components during testing."""
    yield

@pytest.fixture
def mock_dependencies():
    """Mock cache handles and coordinator processes to isolate initializations safely."""
    with patch("custom_components.weerplaza.PersistentCache") as mock_cache_cls, \
         patch("custom_components.weerplaza.WeerplazaCoordinator") as mock_coord_cls:
        
        mock_cache = MagicMock()
        mock_cache.load = AsyncMock(return_value=None)
        mock_cache.clear = AsyncMock()
        mock_cache_cls.return_value = mock_cache

        mock_coord = MagicMock()
        mock_coord._error_count = 0
        mock_coord.cache = mock_cache
        mock_coord.async_config_entry_first_refresh = AsyncMock()
        mock_coord.async_request_refresh = AsyncMock()
        mock_coord_cls.return_value = mock_coord
        
        yield mock_cache, mock_coord


@pytest.mark.asyncio
async def test_async_setup(hass: HomeAssistant):
    """Verify legacy global setups always return true."""
    assert await async_setup(hass, {}) is True


@pytest.mark.asyncio
async def test_setup_entry_no_cache(hass: HomeAssistant, mock_dependencies):
    """Verify system forces first refresh update cleanly when no cache entries exist."""
    mock_cache, mock_coord = mock_dependencies
    entry = MockConfigEntry(domain=DOMAIN, data={"instance_name": "Test", "location_path": "nl/test"})
    entry.add_to_hass(hass)

    with patch("homeassistant.config_entries.ConfigEntries.async_forward_entry_setups", return_value=True):
        assert await async_setup_entry(hass, entry) is True
        mock_coord.async_config_entry_first_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_setup_entry_with_cache(hass: HomeAssistant, mock_dependencies):
    """Verify system shifts to cache configuration profiles if persistent files match."""
    mock_cache, mock_coord = mock_dependencies
    mock_cache.load.return_value = {"current_temperature": 22.5}
    
    entry = MockConfigEntry(domain=DOMAIN, data={"instance_name": "Test", "location_path": "nl/test"})
    entry.add_to_hass(hass)

    with patch("homeassistant.config_entries.ConfigEntries.async_forward_entry_setups", return_value=True):
        assert await async_setup_entry(hass, entry) is True
        mock_coord.async_config_entry_first_refresh.assert_not_called()
        mock_coord.async_set_updated_data.assert_called_once_with({"current_temperature": 22.5})


@pytest.mark.asyncio
async def test_unload_and_reload(hass: HomeAssistant, mock_dependencies):
    """Verify clean tear downs execute structural platform removals completely."""
    mock_cache, mock_coord = mock_dependencies
    entry = MockConfigEntry(domain=DOMAIN, data={"instance_name": "Test", "location_path": "nl/test"})
    entry.add_to_hass(hass)
    
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = mock_coord

    with patch("homeassistant.config_entries.ConfigEntries.async_reload") as mock_reload:
        await async_reload_entry(hass, entry)
        mock_reload.assert_called_once_with(entry.entry_id)

    with patch("homeassistant.config_entries.ConfigEntries.async_unload_platforms", return_value=True) as mock_unload:
        assert await async_unload_entry(hass, entry) is True
        assert entry.entry_id not in hass.data[DOMAIN]


@pytest.mark.asyncio
async def test_custom_service_calls(hass: HomeAssistant, mock_dependencies):
    """Verify utility action registrations pass direct commands to functional boundaries."""
    mock_cache, mock_coord = mock_dependencies
    entry = MockConfigEntry(domain=DOMAIN, data={"instance_name": "Test", "location_path": "nl/test"})
    entry.add_to_hass(hass)

    with patch("homeassistant.config_entries.ConfigEntries.async_forward_entry_setups", return_value=True):
        await async_setup_entry(hass, entry)

    await hass.services.async_call(DOMAIN, "manual_refresh", blocking=True)
    mock_coord.async_request_refresh.assert_called_once()

    await hass.services.async_call(DOMAIN, "clear_cache", blocking=True)
    mock_cache.clear.assert_called_once()
