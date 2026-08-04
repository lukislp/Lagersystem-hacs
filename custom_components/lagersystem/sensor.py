"""Sensor platform for LagerSystem."""
import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
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
    """Set up LagerSystem sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = [
        LagerSystemInventoryValueSensor(coordinator, entry),
        LagerSystemTotalProductsSensor(coordinator, entry),
        LagerSystemLowStockSensor(coordinator, entry),
        LagerSystemExpiryWarningsSensor(coordinator, entry),
        LagerSystemStorageUtilizationSensor(coordinator, entry),
        LagerSystemDailyMovementsSensor(coordinator, entry),
        LagerSystemTopCategoriesSensor(coordinator, entry),
        LagerSystemTotalWarehousesSensor(coordinator, entry),
        LagerSystemTotalRoomsSensor(coordinator, entry),
        LagerSystemTotalStorageLocationsSensor(coordinator, entry),
        LagerSystemTotalUsersSensor(coordinator, entry),
        LagerSystemUnreadNotificationsSensor(coordinator, entry),
        LagerSystemRecentMovementsSensor(coordinator, entry),
        LagerSystemExpiringBatchesSensor(coordinator, entry),
        LagerSystemTotalAuditLogsSensor(coordinator, entry),
        LagerSystemActiveUsersSensor(coordinator, entry),
        LagerSystemWarehouseCapacitySensor(coordinator, entry),
        LagerSystemAverageProductValueSensor(coordinator, entry),
    ]

    add_entities(sensors)


class LagerSystemSensor(CoordinatorEntity, SensorEntity):
    """Base class for LagerSystem sensors."""

    def __init__(self, coordinator, entry, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "LagerSystem",
            "manufacturer": "LagerSystem",
            "model": "Inventory Management",
        }

    def _get_sensor_data(self, entity_id):
        """Get sensor data by entity ID."""
        if self.coordinator.data and "success" in self.coordinator.data:
            data = self.coordinator.data.get("data", [])
            for sensor in data:
                if sensor.get("entityId") == entity_id or sensor.get("entity_id") == entity_id:
                    return sensor
        return None


# ===== EXISTING SENSORS =====

class LagerSystemInventoryValueSensor(LagerSystemSensor):
    """Sensor for total inventory value."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "inventory_value")
        self._attr_name = "Inventory Value"
        self._attr_native_unit_of_measurement = "€"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_icon = "mdi:currency-eur"

    @property
    def native_value(self):
        """Return the state."""
        sensor = self._get_sensor_data("sensor.inventory_total_value")
        return sensor.get("value", 0) if sensor else 0

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_total_value")
        return sensor.get("attributes", {}) if sensor else {}


class LagerSystemTotalProductsSensor(LagerSystemSensor):
    """Sensor for total products."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "total_products")
        self._attr_name = "Total Products"
        self._attr_icon = "mdi:package-variant"

    @property
    def native_value(self):
        """Return the state."""
        sensor = self._get_sensor_data("sensor.inventory_total_products")
        return sensor.get("value", 0) if sensor else 0

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_total_products")
        return sensor.get("attributes", {}) if sensor else {}


class LagerSystemLowStockSensor(LagerSystemSensor):
    """Sensor for low stock count."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "low_stock")
        self._attr_name = "Low Stock Products"
        self._attr_icon = "mdi:alert-circle"

    @property
    def native_value(self):
        """Return the state."""
        sensor = self._get_sensor_data("sensor.inventory_low_stock_count")
        return sensor.get("value", 0) if sensor else 0

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_low_stock_count")
        return sensor.get("attributes", {}) if sensor else {}


class LagerSystemExpiryWarningsSensor(LagerSystemSensor):
    """Sensor for expiry warnings."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "expiry_warnings")
        self._attr_name = "Expiring Products"
        self._attr_icon = "mdi:calendar-alert"

    @property
    def native_value(self):
        """Return the state."""
        sensor = self._get_sensor_data("sensor.inventory_expiry_warnings")
        return sensor.get("value", 0) if sensor else 0

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_expiry_warnings")
        return sensor.get("attributes", {}) if sensor else {}


# ===== NEW SENSORS =====

class LagerSystemStorageUtilizationSensor(LagerSystemSensor):
    """Sensor for storage utilization percentage."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "storage_utilization")
        self._attr_name = "Storage Utilization"
        self._attr_native_unit_of_measurement = "%"
        self._attr_icon = "mdi:warehouse"

    @property
    def native_value(self):
        """Return the state."""
        sensor = self._get_sensor_data("sensor.inventory_storage_utilization")
        return sensor.get("value", 0) if sensor else 0

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_storage_utilization")
        return sensor.get("attributes", {}) if sensor else {}


class LagerSystemDailyMovementsSensor(LagerSystemSensor):
    """Sensor for daily stock movements."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "daily_movements")
        self._attr_name = "Movements Today"
        self._attr_icon = "mdi:swap-horizontal"

    @property
    def native_value(self):
        """Return the state."""
        sensor = self._get_sensor_data("sensor.inventory_daily_movements")
        return sensor.get("value", 0) if sensor else 0

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_daily_movements")
        return sensor.get("attributes", {}) if sensor else {}


class LagerSystemTopCategoriesSensor(LagerSystemSensor):
    """Sensor for top categories."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "top_categories")
        self._attr_name = "Top Categories"
        self._attr_icon = "mdi:tag-multiple"

    @property
    def native_value(self):
        """Return the state."""
        sensor = self._get_sensor_data("sensor.inventory_top_categories")
        return sensor.get("value", 0) if sensor else 0

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_top_categories")
        if sensor:
            attrs = sensor.get("attributes", {})
            # Format categories as list
            if "categories" in attrs:
                attrs["category_list"] = ", ".join(attrs["categories"])
            return attrs
        return {}


# ===== ADDITIONAL ENTITY SENSORS (NEW) =====

class LagerSystemTotalWarehousesSensor(LagerSystemSensor):
    """Sensor for total warehouses count."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "total_warehouses")
        self._attr_name = "Total Warehouses"
        self._attr_icon = "mdi:warehouse"

    @property
    def native_value(self):
        """Return the state."""
        # Get from dashboard or dedicated endpoint
        if self.coordinator.data and "data" in self.coordinator.data:
            # Try to get from warehouses endpoint
            for sensor in self.coordinator.data.get("data", []):
                if sensor.get("entityId") == "sensor.total_warehouses":
                    return sensor.get("value", 0)
        return 0


class LagerSystemTotalRoomsSensor(LagerSystemSensor):
    """Sensor for total rooms count."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "total_rooms")
        self._attr_name = "Total Rooms"
        self._attr_icon = "mdi:door"

    @property
    def native_value(self):
        """Return the state."""
        for sensor in self.coordinator.data.get("data", []):
            if sensor.get("entityId") == "sensor.total_rooms":
                return sensor.get("value", 0)
        return 0


class LagerSystemTotalStorageLocationsSensor(LagerSystemSensor):
    """Sensor for total storage locations count."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "total_storage_locations")
        self._attr_name = "Total Storage Locations"
        self._attr_icon = "mdi:map-marker-multiple"

    @property
    def native_value(self):
        """Return the state."""
        for sensor in self.coordinator.data.get("data", []):
            if sensor.get("entityId") == "sensor.total_storage_locations":
                return sensor.get("value", 0)
        return 0


class LagerSystemTotalUsersSensor(LagerSystemSensor):
    """Sensor for total users count."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "total_users")
        self._attr_name = "Total Users"
        self._attr_icon = "mdi:account-group"

    @property
    def native_value(self):
        """Return the state."""
        for sensor in self.coordinator.data.get("data", []):
            if sensor.get("entityId") == "sensor.total_users":
                return sensor.get("value", 0)
        return 0


class LagerSystemUnreadNotificationsSensor(LagerSystemSensor):
    """Sensor for unread notifications count."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "unread_notifications")
        self._attr_name = "Unread Notifications"
        self._attr_icon = "mdi:bell-badge"

    @property
    def native_value(self):
        """Return the state."""
        for sensor in self.coordinator.data.get("data", []):
            if sensor.get("entityId") == "sensor.unread_notifications":
                return sensor.get("value", 0)
        return 0


class LagerSystemRecentMovementsSensor(LagerSystemSensor):
    """Sensor for recent movements (last hour)."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "recent_movements")
        self._attr_name = "Movements (Last Hour)"
        self._attr_icon = "mdi:clock-fast"

    @property
    def native_value(self):
        """Return the state."""
        for sensor in self.coordinator.data.get("data", []):
            if sensor.get("entityId") == "sensor.recent_movements":
                return sensor.get("value", 0)
        return 0


class LagerSystemExpiringBatchesSensor(LagerSystemSensor):
    """Sensor for expiring batches (next 7 days)."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "expiring_batches")
        self._attr_name = "Expiring Batches"
        self._attr_icon = "mdi:package-variant-closed-remove"

    @property
    def native_value(self):
        """Return the state."""
        for sensor in self.coordinator.data.get("data", []):
            if sensor.get("entityId") == "sensor.expiring_batches":
                return sensor.get("value", 0)
        return 0


class LagerSystemTotalAuditLogsSensor(LagerSystemSensor):
    """Sensor for total audit logs count (last 30 days)."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "total_audit_logs")
        self._attr_name = "Audit Logs (30 Days)"
        self._attr_icon = "mdi:file-document-multiple"

    @property
    def native_value(self):
        """Return the state."""
        for sensor in self.coordinator.data.get("data", []):
            if sensor.get("entityId") == "sensor.total_audit_logs":
                return sensor.get("value", 0)
        return 0


class LagerSystemActiveUsersSensor(LagerSystemSensor):
    """Sensor for active users (logged in last 7 days)."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "active_users")
        self._attr_name = "Active Users"
        self._attr_icon = "mdi:account-check"

    @property
    def native_value(self):
        """Return the state."""
        for sensor in self.coordinator.data.get("data", []):
            if sensor.get("entityId") == "sensor.active_users":
                return sensor.get("value", 0)
        return 0


class LagerSystemWarehouseCapacitySensor(LagerSystemSensor):
    """Sensor for total warehouse capacity."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "warehouse_capacity")
        self._attr_name = "Total Warehouse Capacity"
        self._attr_native_unit_of_measurement = "%"
        self._attr_icon = "mdi:package-variant"

    @property
    def native_value(self):
        """Return the state."""
        for sensor in self.coordinator.data.get("data", []):
            if sensor.get("entityId") == "sensor.warehouse_capacity":
                return sensor.get("value", 0)
        return 0


class LagerSystemAverageProductValueSensor(LagerSystemSensor):
    """Sensor for average product value."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "average_product_value")
        self._attr_name = "Average Product Value"
        self._attr_native_unit_of_measurement = "€"
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_icon = "mdi:calculator"

    @property
    def native_value(self):
        """Return the state."""
        for sensor in self.coordinator.data.get("data", []):
            if sensor.get("entityId") == "sensor.average_product_value":
                return sensor.get("value", 0)
        return 0
