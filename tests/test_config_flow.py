"""Tests for the LagerSystem config flow (single user step)."""
from __future__ import annotations

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lagersystem.const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_VERIFY_SSL,
    DEFAULT_NAME,
    DOMAIN,
)

from .conftest import TEST_API_KEY, TEST_HOST

PATCH_TARGET = "custom_components.lagersystem.config_flow.LagerSystemAPI.test_connection"


async def test_user_step_shows_form(hass: HomeAssistant) -> None:
    """The first call with no input shows the user form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


async def test_user_step_success_creates_entry(hass: HomeAssistant) -> None:
    """A successful connection test creates an entry with the right data/title."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(PATCH_TARGET, return_value=True):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: TEST_HOST, CONF_API_KEY: TEST_API_KEY, CONF_VERIFY_SSL: True},
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == DEFAULT_NAME
    assert result2["data"] == {
        CONF_HOST: TEST_HOST,
        CONF_API_KEY: TEST_API_KEY,
        CONF_VERIFY_SSL: True,
    }


async def test_user_step_success_with_verify_ssl_false(hass: HomeAssistant) -> None:
    """verify_ssl=False submitted by the user flows through into the created entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(PATCH_TARGET, return_value=True):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: TEST_HOST, CONF_API_KEY: TEST_API_KEY, CONF_VERIFY_SSL: False},
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"] == {
        CONF_HOST: TEST_HOST,
        CONF_API_KEY: TEST_API_KEY,
        CONF_VERIFY_SSL: False,
    }


async def test_user_step_cannot_connect(hass: HomeAssistant) -> None:
    """A connection test that returns False re-shows the form with cannot_connect."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(PATCH_TARGET, return_value=False):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: TEST_HOST, CONF_API_KEY: TEST_API_KEY, CONF_VERIFY_SSL: True},
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["step_id"] == "user"
    assert result2["errors"]["base"] == "cannot_connect"


async def test_user_step_unknown_exception(hass: HomeAssistant) -> None:
    """An unexpected exception during the connection test re-shows the form with unknown."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(PATCH_TARGET, side_effect=Exception("boom")):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: TEST_HOST, CONF_API_KEY: TEST_API_KEY, CONF_VERIFY_SSL: True},
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["step_id"] == "user"
    assert result2["errors"]["base"] == "unknown"


async def test_user_step_duplicate_aborts(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Submitting a host/API key pair that's already configured aborts the flow."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(PATCH_TARGET, return_value=True):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_HOST: TEST_HOST, CONF_API_KEY: TEST_API_KEY, CONF_VERIFY_SSL: True},
        )

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"
