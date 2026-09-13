"""Binary sensor platform for LagerSystem."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
        # Entity names are combined with the device name ("LagerSystem Inventory Value",
        # sensor.lagersystem_inventory_value) - the naming Home Assistant expects for entities
        # that belong to a device. Existing installs keep their registered entity ids.
        self._attr_has_entity_name = True
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "LagerSystem",
            "manufacturer": "LagerSystem",
            "model": "Inventory Management",
        }

    def _get_sensor_data(self, entity_id):
        """Get sensor data by entity ID.

        Tolerates any payload shape ({"data": null}, a non-list, non-dict entries): a state
        property that raises takes the entity out of the state machine, so a malformed API
        response must degrade to "no data" instead (found by fuzz/fuzz_sensors.py)."""
        data = self.coordinator.data
        if not isinstance(data, dict) or "success" not in data:
            return None
        entries = data.get("data")
        if not isinstance(entries, list):
            return None
        for sensor in entries:
            if not isinstance(sensor, dict):
                continue
            if (
                sensor.get("entityId") == entity_id
                or sensor.get("entity_id") == entity_id
            ):
                return sensor
        return None


def _as_number(value, default=0.0):
    """The API's numeric value as a float - anything else degrades to ``default``.

    A comparison such as ``value > 0`` raised TypeError for a string value and took the
    entity out of the state machine (found by fuzz/fuzz_sensors.py)."""
    if isinstance(value, bool):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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
            value = _as_number(sensor.get("value", 0))
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
            value = _as_number(sensor.get("value", 0))
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
            value = _as_number(sensor.get("value", 0))
            state = sensor.get("state", "ok")
            return state == "critical" or value >= 90
        return False

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_storage_utilization")
        if sensor:
            attributes = sensor.get("attributes")
            attrs = dict(attributes) if isinstance(attributes, dict) else {}
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
            value = _as_number(sensor.get("value", 0))
            return value > 50
        return False

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        sensor = self._get_sensor_data("sensor.inventory_daily_movements")
        return sensor.get("attributes", {}) if sensor else {}
