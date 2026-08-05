"""Tests for LagerSystemAPI (custom_components/lagersystem/api.py).

Deliberately standalone: aiohttp + aioresponses only, no Home Assistant test
harness (no hass fixture, no pytest_homeassistant_custom_component pieces),
mirroring the fact that api.py itself has zero HA imports - it's a plain
aiohttp.ClientSession wrapper, not a DataUpdateCoordinator.
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import aiohttp
import pytest
import yarl
from aioresponses import aioresponses

from custom_components.lagersystem.api import LagerSystemAPI

TEST_HOST = "https://lager.example.com"
TEST_API_KEY = "test-api-key"


@pytest.fixture
async def session() -> AsyncIterator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession() as s:
        yield s


@pytest.fixture
def api_client(session: aiohttp.ClientSession) -> LagerSystemAPI:
    return LagerSystemAPI(TEST_HOST, TEST_API_KEY, session)


def _calls(m: aioresponses, method: str, url: str) -> list:
    return m.requests[(method, yarl.URL(url))]


# --------------------------------------------------------------------------
# Success path + X-API-Key header, for every GET/POST/DELETE data method.
#
# (method_name, args, http_verb, url_path)
# --------------------------------------------------------------------------

ENDPOINT_CASES = [
    ("get_all_sensors", (), "get", "/api/sensors/all"),
    ("get_alerts_summary", (), "get", "/api/alerts/summary"),
    ("get_analytics_overview", (), "get", "/api/analytics/overview"),
    ("refresh_analytics", (), "post", "/api/analytics/refresh"),
    ("generate_analytics_report", (), "post", "/api/analytics/generate-report"),
    ("get_dashboard_data", (), "get", "/api/dashboard"),
    ("get_warehouses", (), "get", "/api/warehouses"),
    ("get_warehouse_statistics", (7,), "get", "/api/warehouses/7/statistics"),
    ("get_rooms", (), "get", "/api/rooms"),
    ("get_storage_locations", (), "get", "/api/storage-locations"),
    ("get_users", (), "get", "/api/users"),
    ("get_notifications", (), "get", "/api/notifications"),
    ("get_unread_notifications", (), "get", "/api/notifications/unread"),
    ("mark_all_notifications_read", (), "post", "/api/notifications/mark-all-read"),
    ("clear_old_notifications", (), "delete", "/api/notifications/old"),
    ("get_audit_logs", (), "get", "/api/audit-logs"),
    ("export_audit_logs", (), "post", "/api/audit-logs/export"),
    ("clean_old_audit_logs", (), "delete", "/api/audit-logs/old"),
    ("get_recent_movements", (), "get", "/api/movements/recent"),
    ("get_expiring_batches", (), "get", "/api/batches/expiring"),
]


@pytest.mark.parametrize(
    "method_name,args,http_verb,path",
    ENDPOINT_CASES,
    ids=[case[0] for case in ENDPOINT_CASES],
)
async def test_endpoint_success_and_header(
    api_client: LagerSystemAPI, method_name: str, args: tuple, http_verb: str, path: str
) -> None:
    payload = {"result": "ok", "path": path}
    url = f"{TEST_HOST}{path}"
    with aioresponses() as m:
        getattr(m, http_verb)(url, payload=payload, status=200)
        result = await getattr(api_client, method_name)(*args)

    assert result == payload
    calls = _calls(m, http_verb.upper(), url)
    assert len(calls) == 1
    assert calls[0].kwargs["headers"]["X-API-Key"] == TEST_API_KEY


# --------------------------------------------------------------------------
# host trailing-slash stripping
# --------------------------------------------------------------------------


async def test_host_trailing_slash_is_stripped(session: aiohttp.ClientSession) -> None:
    client = LagerSystemAPI(f"{TEST_HOST}/", TEST_API_KEY, session)
    url = f"{TEST_HOST}/api/sensors/all"
    with aioresponses() as m:
        # Mocked with a single slash between host and path. If __init__ failed to
        # strip the trailing slash, the client would request a double-slash URL
        # that doesn't match this mock, and aioresponses would raise instead.
        m.get(url, payload={"ok": True})
        result = await client.get_all_sensors()

    assert result == {"ok": True}
    calls = _calls(m, "GET", url)
    assert len(calls) == 1


# --------------------------------------------------------------------------
# verify_ssl passthrough
# --------------------------------------------------------------------------


async def test_verify_ssl_defaults_true(session: aiohttp.ClientSession) -> None:
    client = LagerSystemAPI(TEST_HOST, TEST_API_KEY, session)
    url = f"{TEST_HOST}/api/sensors/all"
    with aioresponses() as m:
        m.get(url, payload={})
        await client.get_all_sensors()

    calls = _calls(m, "GET", url)
    assert calls[0].kwargs["ssl"] is True


async def test_verify_ssl_false_is_passed_through(session: aiohttp.ClientSession) -> None:
    client = LagerSystemAPI(TEST_HOST, TEST_API_KEY, session, verify_ssl=False)
    url = f"{TEST_HOST}/api/sensors/all"
    with aioresponses() as m:
        m.get(url, payload={"ok": True})
        result = await client.get_all_sensors()

    assert result == {"ok": True}
    calls = _calls(m, "GET", url)
    assert calls[0].kwargs["ssl"] is False


# --------------------------------------------------------------------------
# HTTP error status propagation
# --------------------------------------------------------------------------


async def test_get_raises_client_response_error_on_500(api_client: LagerSystemAPI) -> None:
    with aioresponses() as m:
        m.get(f"{TEST_HOST}/api/sensors/all", status=500)
        with pytest.raises(aiohttp.ClientResponseError):
            await api_client.get_all_sensors()


async def test_post_raises_client_response_error_on_500(api_client: LagerSystemAPI) -> None:
    with aioresponses() as m:
        m.post(f"{TEST_HOST}/api/analytics/refresh", status=500)
        with pytest.raises(aiohttp.ClientResponseError):
            await api_client.refresh_analytics()


async def test_get_raises_client_response_error_on_401(api_client: LagerSystemAPI) -> None:
    with aioresponses() as m:
        m.get(f"{TEST_HOST}/api/rooms", status=401)
        with pytest.raises(aiohttp.ClientResponseError):
            await api_client.get_rooms()


async def test_connection_error_propagates(api_client: LagerSystemAPI) -> None:
    with aioresponses() as m:
        m.get(
            f"{TEST_HOST}/api/sensors/all",
            exception=aiohttp.ClientConnectionError("boom"),
        )
        with pytest.raises(aiohttp.ClientError):
            await api_client.get_all_sensors()


async def test_timeout_error_propagates(api_client: LagerSystemAPI) -> None:
    with aioresponses() as m:
        m.get(f"{TEST_HOST}/api/sensors/all", exception=asyncio.TimeoutError())
        with pytest.raises(asyncio.TimeoutError):
            await api_client.get_all_sensors()


# --------------------------------------------------------------------------
# test_connection
# --------------------------------------------------------------------------


async def test_test_connection_returns_true_on_200(api_client: LagerSystemAPI) -> None:
    with aioresponses() as m:
        m.get(f"{TEST_HOST}/api/sensors/all", payload={"ok": True}, status=200)
        assert await api_client.test_connection() is True


async def test_test_connection_returns_true_on_401(api_client: LagerSystemAPI) -> None:
    with aioresponses() as m:
        m.get(f"{TEST_HOST}/api/sensors/all", status=401)
        assert await api_client.test_connection() is True


async def test_test_connection_returns_false_on_500(api_client: LagerSystemAPI) -> None:
    with aioresponses() as m:
        m.get(f"{TEST_HOST}/api/sensors/all", status=500)
        assert await api_client.test_connection() is False


async def test_test_connection_returns_false_on_connection_error(
    api_client: LagerSystemAPI,
) -> None:
    with aioresponses() as m:
        m.get(
            f"{TEST_HOST}/api/sensors/all",
            exception=aiohttp.ClientConnectionError("boom"),
        )
        assert await api_client.test_connection() is False


async def test_test_connection_sends_api_key_header(api_client: LagerSystemAPI) -> None:
    url = f"{TEST_HOST}/api/sensors/all"
    with aioresponses() as m:
        m.get(url, payload={}, status=200)
        await api_client.test_connection()

    calls = _calls(m, "GET", url)
    assert calls[0].kwargs["headers"]["X-API-Key"] == TEST_API_KEY
