"""Button platform for LagerSystem."""
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    add_entities: AddEntitiesCallback,
) -> None:
    """Set up LagerSystem buttons."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]

    buttons = [
        # Notification Actions
        LagerSystemMarkAllNotificationsReadButton(coordinator, entry, api),
        LagerSystemClearOldNotificationsButton(coordinator, entry, api),

        # Audit Actions
        LagerSystemExportAuditLogsButton(coordinator, entry, api),
        LagerSystemCleanOldAuditLogsButton(coordinator, entry, api),

        # Analytics Actions
        LagerSystemGenerateAnalyticsReportButton(coordinator, entry, api),
        LagerSystemRefreshAnalyticsButton(coordinator, entry, api),

        # Dashboard Actions
        LagerSystemRefreshDashboardButton(coordinator, entry, api),
    ]

    add_entities(buttons)


class LagerSystemButton(CoordinatorEntity, ButtonEntity):
    """Base class for LagerSystem buttons."""

    def __init__(self, coordinator, entry, api, button_type, name, icon):
        """Initialize the button."""
        super().__init__(coordinator)
        self.api = api
        self._attr_unique_id = f"{entry.entry_id}_{button_type}"
        self._attr_name = name
        self._attr_icon = icon
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "LagerSystem",
            "manufacturer": "LagerSystem",
            "model": "Inventory Management",
        }


# ===== NOTIFICATION BUTTONS =====

class LagerSystemMarkAllNotificationsReadButton(LagerSystemButton):
    """Button to mark all notifications as read."""

    def __init__(self, coordinator, entry, api):
        super().__init__(
            coordinator,
            entry,
            api,
            "mark_all_notifications_read",
            "Mark All Notifications Read",
            "mdi:bell-check",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.api.mark_all_notifications_read()
            _LOGGER.info("All notifications marked as read")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(f"Error marking notifications as read: {err}")


class LagerSystemClearOldNotificationsButton(LagerSystemButton):
    """Button to clear old notifications (>30 days)."""

    def __init__(self, coordinator, entry, api):
        super().__init__(
            coordinator,
            entry,
            api,
            "clear_old_notifications",
            "Clear Old Notifications",
            "mdi:bell-remove",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.api.clear_old_notifications()
            _LOGGER.info("Old notifications cleared")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(f"Error clearing old notifications: {err}")


# ===== AUDIT BUTTONS =====

class LagerSystemExportAuditLogsButton(LagerSystemButton):
    """Button to export audit logs."""

    def __init__(self, coordinator, entry, api):
        super().__init__(
            coordinator,
            entry,
            api,
            "export_audit_logs",
            "Export Audit Logs",
            "mdi:file-export",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.api.export_audit_logs()
            _LOGGER.info("Audit logs export initiated")
        except Exception as err:
            _LOGGER.error(f"Error exporting audit logs: {err}")


class LagerSystemCleanOldAuditLogsButton(LagerSystemButton):
    """Button to clean old audit logs (>90 days)."""

    def __init__(self, coordinator, entry, api):
        super().__init__(
            coordinator,
            entry,
            api,
            "clean_old_audit_logs",
            "Clean Old Audit Logs",
            "mdi:delete-sweep",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.api.clean_old_audit_logs()
            _LOGGER.info("Old audit logs cleaned")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(f"Error cleaning old audit logs: {err}")


# ===== ANALYTICS BUTTONS =====

class LagerSystemGenerateAnalyticsReportButton(LagerSystemButton):
    """Button to generate analytics report."""

    def __init__(self, coordinator, entry, api):
        super().__init__(
            coordinator,
            entry,
            api,
            "generate_analytics_report",
            "Generate Analytics Report",
            "mdi:chart-box",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.api.generate_analytics_report()
            _LOGGER.info("Analytics report generation initiated")
        except Exception as err:
            _LOGGER.error(f"Error generating analytics report: {err}")


class LagerSystemRefreshAnalyticsButton(LagerSystemButton):
    """Button to refresh analytics data."""

    def __init__(self, coordinator, entry, api):
        super().__init__(
            coordinator,
            entry,
            api,
            "refresh_analytics",
            "Refresh Analytics",
            "mdi:refresh",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.api.refresh_analytics()
            _LOGGER.info("Analytics data refreshed")
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(f"Error refreshing analytics: {err}")


# ===== DASHBOARD BUTTONS =====

class LagerSystemRefreshDashboardButton(LagerSystemButton):
    """Button to refresh dashboard data."""

    def __init__(self, coordinator, entry, api):
        super().__init__(
            coordinator,
            entry,
            api,
            "refresh_dashboard",
            "Refresh Dashboard",
            "mdi:view-dashboard",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.coordinator.async_request_refresh()
            _LOGGER.info("Dashboard data refreshed")
        except Exception as err:
            _LOGGER.error(f"Error refreshing dashboard: {err}")
