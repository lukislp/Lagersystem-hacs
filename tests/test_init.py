"""Tests for the LagerSystem integration's setup/unload entry points
(custom_components/lagersystem/__init__.py)."""
from __future__ import annotations

import aiohttp
import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lagersystem.api import LagerSystemAPI
from custom_components.lagersystem.const import CONF_API_KEY, CONF_HOST, DOMAIN

from .conftest import TEST_API_KEY, TEST_HOST, make_sensors_payload, setup_integration

# ---------------------------------------------------------------------------
# async_setup_entry - success
# ---------------------------------------------------------------------------


async def test_setup_entry_success(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A successful first refresh loads the entry and stores both the api client
    and the coordinator (with the fetched data) under hass.data[DOMAIN]."""
    payload = make_sensors_payload()

    await setup_integration(hass, monkeypatch, mock_config_entry, get_all_sensors=payload)

    assert mock_config_entry.state is ConfigEntryState.LOADED

    entry_data = hass.data[DOMAIN][mock_config_entry.entry_id]
    assert "api" in entry_data
    assert "coordinator" in entry_data
    assert isinstance(entry_data["api"], LagerSystemAPI)

    coordinator = entry_data["coordinator"]
    assert coordinator.data == payload
    assert coordinator.last_update_success is True


# ---------------------------------------------------------------------------
# async_setup_entry - first refresh failure
# ---------------------------------------------------------------------------


async def test_setup_entry_first_refresh_failure_retries_setup(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """async_update_data() wraps ANY exception raised by get_all_sensors() (there is
    no separate auth-error branch here, unlike the sibling studylife integration) in
    UpdateFailed. When that happens during async_config_entry_first_refresh(), HA's
    own ConfigEntries.async_setup catches the resulting ConfigEntryNotReady and
    schedules a retry instead of loading the entry - this is DataUpdateCoordinator's
    standard behavior, verified by actually running it rather than assumed."""
    monkeypatch.setattr(
        LagerSystemAPI, "get_all_sensors", _raise_client_error
    )
    mock_config_entry.add_to_hass(hass)

    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY
    assert DOMAIN not in hass.data or mock_config_entry.entry_id not in hass.data[DOMAIN]


async def _raise_client_error(self, *args, **kwargs):
    """Stand-in for LagerSystemAPI.get_all_sensors that always fails."""
    raise aiohttp.ClientError("boom")


# ---------------------------------------------------------------------------
# Platforms forwarded
# ---------------------------------------------------------------------------


async def test_setup_entry_forwards_all_platforms(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """After a successful setup, entities exist for all three platforms declared in
    PLATFORMS - a light touch confirming async_forward_entry_setups actually ran for
    sensor/binary_sensor/button; entity-level detail is covered by the sibling
    test_sensor.py/test_binary_sensor.py/test_button.py files."""
    await setup_integration(hass, monkeypatch, mock_config_entry)

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert hass.states.async_entity_ids("sensor")
    assert hass.states.async_entity_ids("binary_sensor")
    assert hass.states.async_entity_ids("button")


# ---------------------------------------------------------------------------
# async_unload_entry
# ---------------------------------------------------------------------------


async def test_unload_entry(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unloading a loaded entry succeeds, flips its state to NOT_LOADED, and pops
    just that entry's key out of hass.data[DOMAIN] - the source only calls
    hass.data[DOMAIN].pop(entry.entry_id), never `del hass.data[DOMAIN]`, so the
    outer DOMAIN dict itself must still exist afterwards (empty)."""
    await setup_integration(hass, monkeypatch, mock_config_entry)
    assert mock_config_entry.entry_id in hass.data[DOMAIN]

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert DOMAIN in hass.data
    assert mock_config_entry.entry_id not in hass.data[DOMAIN]


# ---------------------------------------------------------------------------
# verify_ssl default
# ---------------------------------------------------------------------------


async def test_setup_entry_defaults_verify_ssl_when_absent(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    """entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL) must not KeyError, and
    setup must still succeed, when CONF_VERIFY_SSL is entirely absent from
    entry.data - built manually here since mock_config_entry always includes it."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: TEST_HOST,
            CONF_API_KEY: TEST_API_KEY,
        },
        unique_id=f"{TEST_HOST}_apikey_no_verify_ssl",
    )

    await setup_integration(hass, monkeypatch, entry)

    assert entry.state is ConfigEntryState.LOADED
