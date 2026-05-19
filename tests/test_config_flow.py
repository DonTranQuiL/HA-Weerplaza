import pytest
from unittest.mock import patch
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.weerplaza.const import (
    DOMAIN,
    CONF_INSTANCE_NAME,
    CONF_LOCATION_PATH,
    CONF_SCAN_INTERVAL,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom components during testing."""
    yield


@pytest.mark.asyncio
async def test_config_flow_user_success(hass):
    """Test user step creates configuration entry successfully."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch("custom_components.weerplaza.async_setup_entry", return_value=True):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_INSTANCE_NAME: "Eygelshoven Weather",
                CONF_LOCATION_PATH: "nederland/eygelshoven/9314/",
                CONF_SCAN_INTERVAL: 1800,
                "debug_mode": False,
            },
        )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Eygelshoven Weather"
    assert result2["data"][CONF_LOCATION_PATH] == "nederland/eygelshoven/9314/"


@pytest.mark.asyncio
async def test_options_flow(hass):
    """Test options flow alters scan configuration profiles seamlessly."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_INSTANCE_NAME: "Test", CONF_LOCATION_PATH: "nederland/test/1"},
        options={CONF_SCAN_INTERVAL: 1800, "debug_mode": False},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_SCAN_INTERVAL: 3600,
            "debug_mode": True,
        },
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_SCAN_INTERVAL] == 3600
    assert result2["data"]["debug_mode"] is True
