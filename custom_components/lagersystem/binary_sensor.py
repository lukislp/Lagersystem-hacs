"""Binary sensor platform for LagerSystem."""
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
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
    """Set up LagerSystem binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]

    sensors = [
        LagerSystemLowStockAlert(coordinator, entry, api),
        LagerSystemExpiryAlert(coordinator, entry, api),
        LagerSystemStorageCriticalAlert(coordinator, entry, api),
        LagerSystemHighActivityAlert(coordinator, entry, api),
    ]

    add_entities(sensors)


class LagerSystemBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base class for LagerSystem binary sensors."""

    def __init__(self, coordinator, entry, api, sensor_type):
        super().__init__(coordinator)
        self.api = api
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


# ===== EXISTING BINARY SENSORS =====

class LagerSystemLowStockAlert(LagerSystemBinarySensor):
    """Binary sensor for low stock alert."""

    def __init__(self, coordinator, entry, api):
        super().__init__(coordinator, entry, api, "low_stock_alert")
        self._attr_name = "Low Stock Alert"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_icon = "mdi:alert-circle"

    @property
    def is_on(self):
        """Return true if there are low stock items."""
        sensor = self._get_sensor_data("sensor.inventory_low_stock_count")
        if sensor:
            value = sensor.get("value", 0)
            return value > 0
        return False

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_low_stock_count")
        return sensor.get("attributes", {}) if sensor else {}


class LagerSystemExpiryAlert(LagerSystemBinarySensor):
    """Binary sensor for expiry alert."""

    def __init__(self, coordinator, entry, api):
        super().__init__(coordinator, entry, api, "expiry_alert")
        self._attr_name = "Expiry Alert"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_icon = "mdi:calendar-alert"

    @property
    def is_on(self):
        """Return true if there are expiring items."""
        sensor = self._get_sensor_data("sensor.inventory_expiry_warnings")
        if sensor:
            value = sensor.get("value", 0)
            return value > 0
        return False

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_expiry_warnings")
        return sensor.get("attributes", {}) if sensor else {}


# ===== NEW BINARY SENSORS =====

class LagerSystemStorageCriticalAlert(LagerSystemBinarySensor):
    """Binary sensor for critical storage utilization (>90%)."""

    def __init__(self, coordinator, entry, api):
        super().__init__(coordinator, entry, api, "storage_critical_alert")
        self._attr_name = "Storage Critical Alert"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_icon = "mdi:warehouse"

    @property
    def is_on(self):
        """Return true if storage utilization is critical (>90%)."""
        sensor = self._get_sensor_data("sensor.inventory_storage_utilization")
        if sensor:
            value = sensor.get("value", 0)
            state = sensor.get("state", "ok")
            return state == "critical" or value >= 90
        return False

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_storage_utilization")
        if sensor:
            attrs = sensor.get("attributes", {})
            attrs["utilization_percent"] = sensor.get("value", 0)
            return attrs
        return {}


class LagerSystemHighActivityAlert(LagerSystemBinarySensor):
    """Binary sensor for high activity (>50 movements today)."""

    def __init__(self, coordinator, entry, api):
        super().__init__(coordinator, entry, api, "high_activity_alert")
        self._attr_name = "High Activity Alert"
        self._attr_device_class = BinarySensorDeviceClass.RUNNING
        self._attr_icon = "mdi:swap-horizontal"

    @property
    def is_on(self):
        """Return true if there are high movements today (>50)."""
        sensor = self._get_sensor_data("sensor.inventory_daily_movements")
        if sensor:
            value = sensor.get("value", 0)
            return value > 50
        return False

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_daily_movements")
        return sensor.get("attributes", {}) if sensor else {}
