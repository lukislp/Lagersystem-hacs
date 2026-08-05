"""Shared fixtures and test-data builders for the LagerSystem test suite."""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lagersystem.api import LagerSystemAPI
from custom_components.lagersystem.const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_VERIFY_SSL,
    DOMAIN,
)

pytest_plugins = "pytest_homeassistant_custom_component"

TEST_HOST = "https://lager.example.com"
TEST_API_KEY = "test-api-key"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Make custom_components/ discoverable for every test in this suite."""
    return


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """A config entry matching what the real config flow produces."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: TEST_HOST,
            CONF_API_KEY: TEST_API_KEY,
            CONF_VERIFY_SSL: True,
        },
        unique_id=f"{TEST_HOST}_apikey",
    )


def make_sensor_entry(entity_id: str, value: Any, attributes: dict | None = None) -> dict:
    """Build one entry of the /api/sensors/all "data" list, as the real API returns it."""
    entry: dict[str, Any] = {"entityId": entity_id, "value": value}
    if attributes is not None:
        entry["attributes"] = attributes
    return entry


def make_sensors_payload(*entries: dict) -> dict:
    """Build the full /api/sensors/all response shape: {"success": ..., "data": [...]}."""
    return {"success": True, "data": list(entries)}


async def setup_integration(
    hass,
    monkeypatch: pytest.MonkeyPatch,
    entry: MockConfigEntry,
    *,
    get_all_sensors: dict | None = None,
    test_connection: bool = True,
) -> MockConfigEntry:
    """Patch LagerSystemAPI's network calls and set up a config entry end-to-end.

    Patches the LagerSystemAPI class directly (not HTTP) since the API client is
    constructed internally in async_setup_entry - there's no injection seam to hand
    a pre-built mock client through, unlike the coordinator-based studylife integration.
    """
    monkeypatch.setattr(
        LagerSystemAPI, "test_connection", AsyncMock(return_value=test_connection)
    )
    monkeypatch.setattr(
        LagerSystemAPI,
        "get_all_sensors",
        AsyncMock(
            return_value=get_all_sensors if get_all_sensors is not None else make_sensors_payload()
        ),
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry
