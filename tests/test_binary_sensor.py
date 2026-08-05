"""Tests for the LagerSystem binary_sensor platform
(custom_components/lagersystem/binary_sensor.py).

Unlike test_init.py, these are unit-level tests that instantiate each binary
sensor directly against a Mock coordinator/entry/api - no full hass setup is
needed since _get_sensor_data() reads straight off self.coordinator.data, and
none of these entities depend on hass wiring (entity registry, dynamic
discovery, etc). This mirrors the defensive unit test at the bottom of the
sibling studylife integration's test_binary_sensor.py, just applied to every
case here rather than only the "missing data" one.

make_sensor_entry()/make_sensors_payload() (from conftest) build the
coordinator.data payload shape exactly as the real API returns it. The one
exception is LagerSystemStorageCriticalAlert's "state" field, which
make_sensor_entry() doesn't know about (it only takes entity_id/value/
attributes) - for those cases we extend the returned dict locally with
entry["state"] = ... before wrapping it in make_sensors_payload().
"""
from __future__ import annotations

from unittest.mock import Mock

from homeassistant.components.binary_sensor import BinarySensorDeviceClass

from custom_components.lagersystem.binary_sensor import (
    LagerSystemExpiryAlert,
    LagerSystemHighActivityAlert,
    LagerSystemLowStockAlert,
    LagerSystemStorageCriticalAlert,
)

from .conftest import make_sensor_entry, make_sensors_payload

LOW_STOCK_ENTITY_ID = "sensor.inventory_low_stock_count"
EXPIRY_ENTITY_ID = "sensor.inventory_expiry_warnings"
STORAGE_ENTITY_ID = "sensor.inventory_storage_utilization"
DAILY_MOVEMENTS_ENTITY_ID = "sensor.inventory_daily_movements"


def _make_coordinator(data: dict | None) -> Mock:
    """A stand-in DataUpdateCoordinator exposing just .data, as _get_sensor_data reads it."""
    coordinator = Mock()
    coordinator.data = data
    return coordinator


def _make_entry() -> Mock:
    """A stand-in ConfigEntry - only entry_id is read (for unique_id/device_info)."""
    entry = Mock()
    entry.entry_id = "test_entry_id"
    return entry


# ---------------------------------------------------------------------------
# LagerSystemLowStockAlert
# ---------------------------------------------------------------------------


def test_low_stock_alert_on_when_value_positive() -> None:
    payload = make_sensors_payload(make_sensor_entry(LOW_STOCK_ENTITY_ID, 3))
    entity = LagerSystemLowStockAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is True


def test_low_stock_alert_off_when_value_zero() -> None:
    payload = make_sensors_payload(make_sensor_entry(LOW_STOCK_ENTITY_ID, 0))
    entity = LagerSystemLowStockAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is False


def test_low_stock_alert_off_when_sensor_missing() -> None:
    payload = make_sensors_payload()
    entity = LagerSystemLowStockAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is False
    assert entity.extra_state_attributes == {}


# ---------------------------------------------------------------------------
# LagerSystemExpiryAlert
# ---------------------------------------------------------------------------


def test_expiry_alert_on_when_value_positive() -> None:
    payload = make_sensors_payload(make_sensor_entry(EXPIRY_ENTITY_ID, 2))
    entity = LagerSystemExpiryAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is True


def test_expiry_alert_off_when_value_zero() -> None:
    payload = make_sensors_payload(make_sensor_entry(EXPIRY_ENTITY_ID, 0))
    entity = LagerSystemExpiryAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is False


def test_expiry_alert_off_when_sensor_missing() -> None:
    payload = make_sensors_payload()
    entity = LagerSystemExpiryAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is False
    assert entity.extra_state_attributes == {}


# ---------------------------------------------------------------------------
# LagerSystemStorageCriticalAlert - state=="critical" OR value>=90, independently
# ---------------------------------------------------------------------------


def test_storage_critical_alert_on_when_value_at_threshold_and_state_critical() -> None:
    """The "normal" case: both the state and value paths agree it's critical."""
    entry = make_sensor_entry(STORAGE_ENTITY_ID, 95)
    entry["state"] = "critical"
    payload = make_sensors_payload(entry)
    entity = LagerSystemStorageCriticalAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is True


def test_storage_critical_alert_off_when_below_threshold_and_state_ok() -> None:
    entry = make_sensor_entry(STORAGE_ENTITY_ID, 50)
    entry["state"] = "ok"
    payload = make_sensors_payload(entry)
    entity = LagerSystemStorageCriticalAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is False


def test_storage_critical_alert_off_when_sensor_missing() -> None:
    payload = make_sensors_payload()
    entity = LagerSystemStorageCriticalAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is False
    assert entity.extra_state_attributes == {}


def test_storage_critical_alert_on_when_state_critical_but_value_below_threshold() -> None:
    """state=="critical" alone is sufficient, even if value hasn't crossed 90."""
    entry = make_sensor_entry(STORAGE_ENTITY_ID, 40)
    entry["state"] = "critical"
    payload = make_sensors_payload(entry)
    entity = LagerSystemStorageCriticalAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is True


def test_storage_critical_alert_on_when_value_above_threshold_but_state_ok() -> None:
    """value>=90 alone is sufficient, even if state says something else (e.g. "ok")."""
    entry = make_sensor_entry(STORAGE_ENTITY_ID, 90)
    entry["state"] = "ok"
    payload = make_sensors_payload(entry)
    entity = LagerSystemStorageCriticalAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is True


def test_storage_critical_alert_on_when_value_above_threshold_and_state_absent() -> None:
    """Same value-only path, but with "state" entirely absent from the payload
    (falls back to the "ok" default inside is_on) rather than explicitly "ok"."""
    payload = make_sensors_payload(make_sensor_entry(STORAGE_ENTITY_ID, 92))
    entity = LagerSystemStorageCriticalAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is True


def test_storage_critical_alert_extra_state_attributes_injects_utilization_percent() -> None:
    entry = make_sensor_entry(STORAGE_ENTITY_ID, 77, attributes={"warehouse": "main"})
    entry["state"] = "ok"
    payload = make_sensors_payload(entry)
    entity = LagerSystemStorageCriticalAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.extra_state_attributes == {"warehouse": "main", "utilization_percent": 77}


# ---------------------------------------------------------------------------
# LagerSystemHighActivityAlert
# ---------------------------------------------------------------------------


def test_high_activity_alert_on_when_value_above_threshold() -> None:
    payload = make_sensors_payload(make_sensor_entry(DAILY_MOVEMENTS_ENTITY_ID, 51))
    entity = LagerSystemHighActivityAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is True


def test_high_activity_alert_off_when_value_at_threshold() -> None:
    """Boundary check: exactly 50 does not satisfy the strict ">50" condition."""
    payload = make_sensors_payload(make_sensor_entry(DAILY_MOVEMENTS_ENTITY_ID, 50))
    entity = LagerSystemHighActivityAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is False


def test_high_activity_alert_off_when_sensor_missing() -> None:
    payload = make_sensors_payload()
    entity = LagerSystemHighActivityAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.is_on is False
    assert entity.extra_state_attributes == {}


# ---------------------------------------------------------------------------
# device_class spot checks
# ---------------------------------------------------------------------------


def test_low_stock_alert_device_class_is_problem() -> None:
    payload = make_sensors_payload()
    entity = LagerSystemLowStockAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.device_class == BinarySensorDeviceClass.PROBLEM


def test_high_activity_alert_device_class_is_running() -> None:
    payload = make_sensors_payload()
    entity = LagerSystemHighActivityAlert(_make_coordinator(payload), _make_entry(), Mock())

    assert entity.device_class == BinarySensorDeviceClass.RUNNING
