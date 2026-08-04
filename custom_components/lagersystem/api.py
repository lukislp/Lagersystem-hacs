"""API Client for LagerSystem."""
import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout

from .const import (
    ENDPOINT_SENSORS_ALL,
    ENDPOINT_ALERTS_SUMMARY,
    ENDPOINT_ANALYTICS_OVERVIEW,
    ENDPOINT_DASHBOARD_DATA,
    ENDPOINT_WAREHOUSES,
    ENDPOINT_ROOMS,
    ENDPOINT_STORAGE_LOCATIONS,
    ENDPOINT_USERS,
    ENDPOINT_NOTIFICATIONS,
    ENDPOINT_NOTIFICATIONS_UNREAD,
    ENDPOINT_NOTIFICATIONS_MARK_ALL_READ,
    ENDPOINT_AUDIT_LOGS,
    ENDPOINT_AUDIT_LOGS_EXPORT,
    ENDPOINT_MOVEMENTS_RECENT,
    ENDPOINT_BATCHES_EXPIRING,
)

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10


class LagerSystemAPI:
    """API client for LagerSystem."""

    def __init__(
        self,
        host: str,
        api_key: str,
        session: aiohttp.ClientSession,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize the API client."""
        self.host = host.rstrip("/")
        self.api_key = api_key
        self.session = session
        self.verify_ssl = verify_ssl

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make a request to the API."""
        url = f"{self.host}{endpoint}"
        headers = kwargs.pop("headers", {})
        headers["X-API-Key"] = self.api_key

        # Certificate verification is on by default; users with a self-signed
        # certificate can opt out explicitly via the "Verify SSL certificate"
        # option in the integration's configuration.
        if "ssl" not in kwargs:
            kwargs["ssl"] = self.verify_ssl

        try:
            async with async_timeout.timeout(TIMEOUT):
                async with self.session.request(
                    method, url, headers=headers, **kwargs
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to LagerSystem API: %s", err)
            raise
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout connecting to LagerSystem API")
            raise

    # ===== SENSORS =====

    async def get_all_sensors(self) -> dict[str, Any]:
        """Get all sensor data."""
        return await self._request("GET", ENDPOINT_SENSORS_ALL)

    # ===== ALERTS =====

    async def get_alerts_summary(self) -> dict[str, Any]:
        """Get alerts summary."""
        return await self._request("GET", ENDPOINT_ALERTS_SUMMARY)

    # ===== ANALYTICS =====

    async def get_analytics_overview(self) -> dict[str, Any]:
        """Get analytics overview."""
        return await self._request("GET", ENDPOINT_ANALYTICS_OVERVIEW)

    async def refresh_analytics(self) -> dict[str, Any]:
        """Refresh analytics data."""
        return await self._request("POST", "/api/analytics/refresh")

    async def generate_analytics_report(self) -> dict[str, Any]:
        """Generate analytics report."""
        return await self._request("POST", "/api/analytics/generate-report")

    # ===== DASHBOARD =====

    async def get_dashboard_data(self) -> dict[str, Any]:
        """Get dashboard data."""
        return await self._request("GET", ENDPOINT_DASHBOARD_DATA)

    # ===== WAREHOUSES =====

    async def get_warehouses(self) -> dict[str, Any]:
        """Get all warehouses."""
        return await self._request("GET", ENDPOINT_WAREHOUSES)

    async def get_warehouse_statistics(self, warehouse_id: int) -> dict[str, Any]:
        """Get warehouse statistics."""
        return await self._request("GET", f"/api/warehouses/{warehouse_id}/statistics")

    # ===== ROOMS =====

    async def get_rooms(self) -> dict[str, Any]:
        """Get all rooms."""
        return await self._request("GET", ENDPOINT_ROOMS)

    # ===== STORAGE LOCATIONS =====

    async def get_storage_locations(self) -> dict[str, Any]:
        """Get all storage locations."""
        return await self._request("GET", ENDPOINT_STORAGE_LOCATIONS)

    # ===== USERS =====

    async def get_users(self) -> dict[str, Any]:
        """Get all users."""
        return await self._request("GET", ENDPOINT_USERS)

    # ===== NOTIFICATIONS =====

    async def get_notifications(self) -> dict[str, Any]:
        """Get all notifications."""
        return await self._request("GET", ENDPOINT_NOTIFICATIONS)

    async def get_unread_notifications(self) -> dict[str, Any]:
        """Get unread notifications."""
        return await self._request("GET", ENDPOINT_NOTIFICATIONS_UNREAD)

    async def mark_all_notifications_read(self) -> dict[str, Any]:
        """Mark all notifications as read."""
        return await self._request("POST", ENDPOINT_NOTIFICATIONS_MARK_ALL_READ)

    async def clear_old_notifications(self) -> dict[str, Any]:
        """Clear old notifications (>30 days)."""
        return await self._request("DELETE", "/api/notifications/old")

    # ===== AUDIT LOGS =====

    async def get_audit_logs(self) -> dict[str, Any]:
        """Get audit logs."""
        return await self._request("GET", ENDPOINT_AUDIT_LOGS)

    async def export_audit_logs(self) -> dict[str, Any]:
        """Export audit logs."""
        return await self._request("POST", ENDPOINT_AUDIT_LOGS_EXPORT)

    async def clean_old_audit_logs(self) -> dict[str, Any]:
        """Clean old audit logs (>90 days)."""
        return await self._request("DELETE", "/api/audit-logs/old")

    # ===== MOVEMENTS =====

    async def get_recent_movements(self) -> dict[str, Any]:
        """Get recent movements."""
        return await self._request("GET", ENDPOINT_MOVEMENTS_RECENT)

    # ===== BATCHES =====

    async def get_expiring_batches(self) -> dict[str, Any]:
        """Get expiring batches."""
        return await self._request("GET", ENDPOINT_BATCHES_EXPIRING)

    # ===== CONNECTION TEST =====

    async def test_connection(self) -> bool:
        """Test the connection to the API."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                async with self.session.get(
                    f"{self.host}/api/sensors/all",
                    headers={"X-API-Key": self.api_key},
                    ssl=self.verify_ssl,
                ) as response:
                    # Accept both 200 (success) and 401 (unauthorized but reachable)
                    return response.status in [200, 401]
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False
