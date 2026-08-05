"""Tests for the LagerSystem button platform (custom_components/lagersystem/button.py).

button.py defines 7 CoordinatorEntity + ButtonEntity subclasses, each wrapping
(at most) one api.* call in async_press:

- MarkAllNotificationsRead, ClearOldNotifications, CleanOldAuditLogs and
  RefreshAnalytics call one api.* method and then
  `await self.coordinator.async_request_refresh()`.
- ExportAuditLogs and GenerateAnalyticsReport call one api.* method but do
  NOT refresh afterward.
- RefreshDashboard calls no api.* method at all - it only refreshes.

Every async_press wraps its body in a bare `try/except Exception as err:
_LOGGER.error(...)`, so pressing a button never raises even when the
underlying api call (or the refresh itself) fails - that's asserted directly
below rather than assumed. Because the refresh line always comes *after* the
api call inside the try block, a failing api call also means no refresh is
attempted, for every button that would otherwise refresh.

This suite:
1. Confirms all 7 entity_ids HA generates (slugified from _attr_name).
2. For the 6 api-calling buttons, presses each and asserts the correct
   api.* method was awaited exactly once.
3. For the same 6, presses each with the api method raising and asserts the
   press does not raise, and that no refresh is attempted in that case.
4. For the 4 buttons that refresh on success, spies on
   coordinator.async_request_refresh (wrapping the real implementation, so
   coordinator.data still updates) and asserts it fires after a successful
   press.
5. For the 2 buttons that never refresh (ExportAuditLogs,
   GenerateAnalyticsReport), asserts the refresh spy stays untouched even on
   a successful press.
6. For RefreshDashboard, asserts a refresh happens with no api.* method
   touched at all, and that a failing refresh is swallowed too.
"""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lagersystem.api import LagerSystemAPI
from custom_components.lagersystem.const import DOMAIN

from .conftest import setup_integration

# ---------------------------------------------------------------------------
# entity_id -> api method name, for the 6 buttons that call exactly one api
# method. entity_id is what Home Assistant actually generates from each
# button's _attr_name via slugification - confirmed by running this suite
# once and reading hass.states.async_entity_ids("button") rather than
# guessed blindly.
# ---------------------------------------------------------------------------

BUTTON_API_METHOD: dict[str, str] = {
    "button.mark_all_notifications_read": "mark_all_notifications_read",
    "button.clear_old_notifications": "clear_old_notifications",
    "button.export_audit_logs": "export_audit_logs",
    "button.clean_old_audit_logs": "clean_old_audit_logs",
    "button.generate_analytics_report": "generate_analytics_report",
    "button.refresh_analytics": "refresh_analytics",
}

REFRESH_DASHBOARD_ENTITY_ID = "button.refresh_dashboard"

# Buttons that call coordinator.async_request_refresh() after a successful api call.
REFRESHING_ENTITY_IDS = sorted(
    {
        "button.mark_all_notifications_read",
        "button.clear_old_notifications",
        "button.clean_old_audit_logs",
        "button.refresh_analytics",
    }
)

# Buttons that call an api method but never refresh afterward, even on success.
NON_REFRESHING_ENTITY_IDS = sorted(
    {
        "button.export_audit_logs",
        "button.generate_analytics_report",
    }
)

ALL_BUTTON_ENTITY_IDS = set(BUTTON_API_METHOD) | {REFRESH_DASHBOARD_ENTITY_ID}


def _mock_api_method(monkeypatch: pytest.MonkeyPatch, method_name: str, **kwargs) -> AsyncMock:
    """Patch one LagerSystemAPI method (class-level, matching conftest's
    setup_integration pattern) with an AsyncMock and return it."""
    mock = AsyncMock(**kwargs)
    monkeypatch.setattr(LagerSystemAPI, method_name, mock)
    return mock


def _spy_on_refresh(monkeypatch: pytest.MonkeyPatch, coordinator) -> AsyncMock:
    """Wrap coordinator.async_request_refresh with an AsyncMock spy that still
    calls through to the real bound method, so refresh side effects (like
    coordinator.data updates) still happen - only the instance is patched,
    not the DataUpdateCoordinator class."""
    real_refresh = coordinator.async_request_refresh
    spy = AsyncMock(side_effect=real_refresh)
    monkeypatch.setattr(coordinator, "async_request_refresh", spy)
    return spy


async def _press(hass: HomeAssistant, entity_id: str) -> None:
    await hass.services.async_call(
        "button", "press", {"entity_id": entity_id}, blocking=True
    )


# ---------------------------------------------------------------------------
# Entity IDs generated
# ---------------------------------------------------------------------------


async def test_all_7_button_entities_created(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """async_setup_entry adds exactly the 7 buttons listed in button.py's
    `buttons` list, and HA's slugification of each _attr_name produces the
    entity_ids this suite's tables assume."""
    await setup_integration(hass, monkeypatch, mock_config_entry)

    actual_entity_ids = set(hass.states.async_entity_ids("button"))
    assert actual_entity_ids == ALL_BUTTON_ENTITY_IDS


# ---------------------------------------------------------------------------
# Each api-calling button calls its api method exactly once on press
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entity_id,method_name", sorted(BUTTON_API_METHOD.items()))
async def test_button_calls_correct_api_method(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    monkeypatch: pytest.MonkeyPatch,
    entity_id: str,
    method_name: str,
) -> None:
    await setup_integration(hass, monkeypatch, mock_config_entry)
    api_mock = _mock_api_method(monkeypatch, method_name, return_value={})

    await _press(hass, entity_id)

    api_mock.assert_awaited_once()


# ---------------------------------------------------------------------------
# Exceptions from the api call are swallowed - press never raises, and the
# refresh that would otherwise follow is never reached.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entity_id,method_name", sorted(BUTTON_API_METHOD.items()))
async def test_button_swallows_api_exception(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    monkeypatch: pytest.MonkeyPatch,
    entity_id: str,
    method_name: str,
) -> None:
    await setup_integration(hass, monkeypatch, mock_config_entry)
    coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]["coordinator"]
    refresh_spy = _spy_on_refresh(monkeypatch, coordinator)
    api_mock = _mock_api_method(monkeypatch, method_name, side_effect=Exception("boom"))

    # Must not raise - async_press wraps the api call in try/except Exception.
    await _press(hass, entity_id)

    api_mock.assert_awaited_once()
    # The refresh call sits after the api call inside the same try block, so
    # a raising api call means it's never reached - true for all 6 buttons,
    # including the 2 that wouldn't refresh even on success.
    refresh_spy.assert_not_awaited()


# ---------------------------------------------------------------------------
# Refresh behavior after a successful press
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("entity_id", REFRESHING_ENTITY_IDS)
async def test_refreshing_button_triggers_coordinator_refresh_on_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    monkeypatch: pytest.MonkeyPatch,
    entity_id: str,
) -> None:
    await setup_integration(hass, monkeypatch, mock_config_entry)
    coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]["coordinator"]
    refresh_spy = _spy_on_refresh(monkeypatch, coordinator)
    _mock_api_method(monkeypatch, BUTTON_API_METHOD[entity_id], return_value={})

    await _press(hass, entity_id)

    refresh_spy.assert_awaited_once()


@pytest.mark.parametrize("entity_id", NON_REFRESHING_ENTITY_IDS)
async def test_non_refreshing_button_does_not_trigger_refresh_on_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    monkeypatch: pytest.MonkeyPatch,
    entity_id: str,
) -> None:
    """ExportAuditLogsButton and GenerateAnalyticsReportButton both call their
    api method successfully but, unlike the other 4 api-calling buttons,
    never follow up with coordinator.async_request_refresh() - a real,
    intentional-looking behavioral difference from their siblings, asserted
    explicitly rather than left as an unchecked omission."""
    await setup_integration(hass, monkeypatch, mock_config_entry)
    coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]["coordinator"]
    refresh_spy = _spy_on_refresh(monkeypatch, coordinator)
    api_mock = _mock_api_method(monkeypatch, BUTTON_API_METHOD[entity_id], return_value={})

    await _press(hass, entity_id)

    api_mock.assert_awaited_once()
    refresh_spy.assert_not_awaited()


# ---------------------------------------------------------------------------
# RefreshDashboardButton - no api.* call at all, just a coordinator refresh
# ---------------------------------------------------------------------------


async def test_refresh_dashboard_button_refreshes_without_calling_any_api_method(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await setup_integration(hass, monkeypatch, mock_config_entry)
    coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]["coordinator"]
    refresh_spy = _spy_on_refresh(monkeypatch, coordinator)

    # Mock every other button's api method so a stray, unexpected call would
    # be caught by the assertions below instead of silently hitting the
    # (unpatched, network-backed) real LagerSystemAPI methods.
    other_api_mocks = [
        _mock_api_method(monkeypatch, method_name, return_value={})
        for method_name in BUTTON_API_METHOD.values()
    ]

    await _press(hass, REFRESH_DASHBOARD_ENTITY_ID)

    refresh_spy.assert_awaited_once()
    for api_mock in other_api_mocks:
        api_mock.assert_not_awaited()


async def test_refresh_dashboard_button_swallows_refresh_exception(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RefreshDashboardButton has no api.* call to fail, but its
    async_request_refresh() call is itself wrapped by the same bare
    try/except - confirmed here by making the refresh itself raise."""
    await setup_integration(hass, monkeypatch, mock_config_entry)
    coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]["coordinator"]
    refresh_spy = AsyncMock(side_effect=Exception("boom"))
    monkeypatch.setattr(coordinator, "async_request_refresh", refresh_spy)

    # Must not raise.
    await _press(hass, REFRESH_DASHBOARD_ENTITY_ID)

    refresh_spy.assert_awaited_once()
