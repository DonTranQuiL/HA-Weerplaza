import pytest
from unittest.mock import MagicMock
from homeassistant.const import EntityCategory
from custom_components.weerplaza.sensor import (
    WeerplazaMasterSensor,
    WeerplazaDiagnosticSensor,
)


@pytest.fixture
def mock_coordinator():
    coord = MagicMock()
    coord._error_count = 0
    coord.data = {
        "current_temperature": 16.5,
        "laatste_scrape_tijd": "19-05-2026 13:00:00",
        "rain": "Droog",
    }
    return coord


def test_master_weather_sensor(mock_coordinator):
    """Verify core attributes map completely to entities."""
    dev_info = MagicMock()
    sensor = WeerplazaMasterSensor(mock_coordinator, "Home", "home", dev_info)

    assert sensor.native_value == 16.5
    assert sensor.extra_state_attributes["rain"] == "Droog"
    assert sensor.unique_id == "home_master_weather"


def test_diagnostic_sensors(mock_coordinator):
    """Verify tracking attributes map data points cleanly onto structural categories."""
    dev_info = MagicMock()
    status_sensor = WeerplazaDiagnosticSensor(
        mock_coordinator, "Home", "home", dev_info, "Status"
    )
    update_sensor = WeerplazaDiagnosticSensor(
        mock_coordinator, "Home", "home", dev_info, "Laatste Update"
    )

    assert status_sensor.native_value == "OK"
    assert update_sensor.native_value == "19-05-2026 13:00:00"
    assert status_sensor.entity_category == EntityCategory.DIAGNOSTIC

    mock_coordinator._error_count = 1
    assert status_sensor.native_value == "Fout"

    # Test cache notification string fallback matches exactly
    mock_coordinator.data = {"current_temperature": 12}
    assert update_sensor.native_value == "Uit Cache (Wacht op timer)"
