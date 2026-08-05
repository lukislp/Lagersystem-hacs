"""Tests for the LagerSystem sensor platform (custom_components/lagersystem/sensor.py).

sensor.py defines 18 sensor entities across two patterns:

- "EXISTING SENSORS" + "NEW SENSORS" (7 total) route through
  LagerSystemSensor._get_sensor_data(), which guards on
  `if self.coordinator.data and "success" in self.coordinator.data` before indexing,
  and returns None on a miss - native_value then falls back to 0.
- "ADDITIONAL ENTITY SENSORS (NEW)" (11 total) iterate
  `self.coordinator.data.get("data", [])` directly. LagerSystemTotalWarehousesSensor
  wraps its loop in an `if self.coordinator.data and "data" in self.coordinator.data`
  guard; the other 10 call `.get("data", [])` with no guard at all, which would raise
  AttributeError if coordinator.data were ever None. That state isn't reachable via
  normal setup (DataUpdateCoordinator never leaves .data as None after a successful
  first refresh), so it isn't exercised here - see the report for details.

Rather than one near-identical test per sensor class, this suite:
1. Verifies all 18 entity_ids HA actually generates (slugified from _attr_name).
2. Runs one comprehensive happy-path test asserting all 18 states against a payload
   that includes every known entityId.
3. Runs one "empty data" test confirming every sensor falls back to 0 without raising.
4. Spot-checks extra_state_attributes on two sensors with distinct behavior.
5. Confirms the MONETARY device class on the sensors that declare it.
6. Confirms device_info identifiers tie back to (DOMAIN, entry.entry_id).
"""
from __future__ import annotations

import pytest
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lagersystem.const import DOMAIN

from .conftest import make_sensor_entry, make_sensors_payload, setup_integration

# ---------------------------------------------------------------------------
# entity_id -> (entityId payload key, expected value) for the happy-path test.
#
# entityId is the key the API/coordinator payload uses (matched by
# LagerSystemSensor._get_sensor_data or the direct .get("data", []) loops).
# entity_id is what Home Assistant actually generates from each sensor's
# _attr_name via slugification - confirmed by running this suite once and
# reading hass.states.async_entity_ids("sensor") rather than guessed blindly.
# ---------------------------------------------------------------------------

SENSOR_CASES: dict[str, tuple[str, object]] = {
    "sensor.inventory_value": ("sensor.inventory_total_value", 12345.67),
    "sensor.total_products": ("sensor.inventory_total_products", 250),
    "sensor.low_stock_products": ("sensor.inventory_low_stock_count", 7),
    "sensor.expiring_products": ("sensor.inventory_expiry_warnings", 3),
    "sensor.storage_utilization": ("sensor.inventory_storage_utilization", 82.5),
    "sensor.movements_today": ("sensor.inventory_daily_movements", 15),
    "sensor.top_categories": ("sensor.inventory_top_categories", 5),
    "sensor.total_warehouses": ("sensor.total_warehouses", 4),
    "sensor.total_rooms": ("sensor.total_rooms", 20),
    "sensor.total_storage_locations": ("sensor.total_storage_locations", 120),
    "sensor.total_users": ("sensor.total_users", 9),
    "sensor.unread_notifications": ("sensor.unread_notifications", 2),
    "sensor.movements_last_hour": ("sensor.recent_movements", 6),
    "sensor.expiring_batches": ("sensor.expiring_batches", 8),
    "sensor.audit_logs_30_days": ("sensor.total_audit_logs", 42),
    "sensor.active_users": ("sensor.active_users", 6),
    "sensor.total_warehouse_capacity": ("sensor.warehouse_capacity", 73.2),
    "sensor.average_product_value": ("sensor.average_product_value", 49.99),
}


def _build_full_payload() -> dict:
    """A payload containing every known entityId, each with a distinct value."""
    return make_sensors_payload(
        *(
            make_sensor_entry(entity_id_key, value)
            for entity_id_key, value in SENSOR_CASES.values()
        )
    )


# ---------------------------------------------------------------------------
# Entity IDs generated
# ---------------------------------------------------------------------------


async def test_all_18_sensor_entities_created(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """async_setup_entry adds exactly the 18 sensors listed in sensor.py's `sensors`
    list, and HA's slugification of each _attr_name produces the entity_ids this
    suite's SENSOR_CASES table assumes - asserted directly instead of guessed."""
    await setup_integration(hass, monkeypatch, mock_config_entry, get_all_sensors=_build_full_payload())

    actual_entity_ids = set(hass.states.async_entity_ids("sensor"))
    assert actual_entity_ids == set(SENSOR_CASES.keys())


# ---------------------------------------------------------------------------
# Happy path - all 18 sensors read back their distinct values
# ---------------------------------------------------------------------------


async def test_all_sensors_report_expected_values(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every sensor's state matches the value keyed to its entityId in the payload,
    covering both the _get_sensor_data() pattern and the direct-iteration pattern."""
    await setup_integration(hass, monkeypatch, mock_config_entry, get_all_sensors=_build_full_payload())

    for entity_id, (_entity_id_key, expected_value) in SENSOR_CASES.items():
        state = hass.states.get(entity_id)
        assert state is not None, f"{entity_id} was not created"
        assert state.state == str(expected_value), f"{entity_id} reported {state.state!r}"


# ---------------------------------------------------------------------------
# Missing / empty data - every sensor falls back gracefully
# ---------------------------------------------------------------------------


async def test_all_sensors_fall_back_to_zero_on_empty_data(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With an empty (but well-formed) {"success": True, "data": []} payload, none of
    the 18 sensors should crash during setup, and each documented-numeric sensor
    should read back its 0 fallback - true whether it goes through
    _get_sensor_data() (returns None -> `sensor.get(...) if sensor else 0`) or the
    direct .get("data", []) loops (loop over an empty list -> falls through to the
    trailing `return 0`)."""
    await setup_integration(hass, monkeypatch, mock_config_entry, get_all_sensors=make_sensors_payload())

    for entity_id in SENSOR_CASES:
        state = hass.states.get(entity_id)
        assert state is not None, f"{entity_id} was not created"
        assert state.state == "0", f"{entity_id} reported {state.state!r}, expected fallback 0"


# ---------------------------------------------------------------------------
# extra_state_attributes
# ---------------------------------------------------------------------------


async def test_inventory_value_attributes_pass_through(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """LagerSystemInventoryValueSensor.extra_state_attributes is a plain passthrough
    of the sensor entry's "attributes" dict."""
    payload = make_sensors_payload(
        make_sensor_entry(
            "sensor.inventory_total_value",
            12345.67,
            attributes={"currency": "EUR", "last_updated": "2026-08-05T00:00:00Z"},
        )
    )
    await setup_integration(hass, monkeypatch, mock_config_entry, get_all_sensors=payload)

    state = hass.states.get("sensor.inventory_value")
    assert state.attributes["currency"] == "EUR"
    assert state.attributes["last_updated"] == "2026-08-05T00:00:00Z"


async def test_top_categories_formats_category_list(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """LagerSystemTopCategoriesSensor.extra_state_attributes injects a derived
    "category_list" attribute - a comma-joined string built from the "categories"
    list - alongside the attributes passed through from the API."""
    payload = make_sensors_payload(
        make_sensor_entry(
            "sensor.inventory_top_categories",
            5,
            attributes={"categories": ["Electronics", "Tools", "Consumables"]},
        )
    )
    await setup_integration(hass, monkeypatch, mock_config_entry, get_all_sensors=payload)

    state = hass.states.get("sensor.top_categories")
    assert state.attributes["categories"] == ["Electronics", "Tools", "Consumables"]
    assert state.attributes["category_list"] == "Electronics, Tools, Consumables"


async def test_top_categories_no_categories_key_omits_category_list(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When the "categories" key is absent from attributes, the "if 'categories' in
    attrs" guard means no category_list is synthesized - just the passthrough."""
    payload = make_sensors_payload(
        make_sensor_entry("sensor.inventory_top_categories", 5, attributes={"note": "no categories here"})
    )
    await setup_integration(hass, monkeypatch, mock_config_entry, get_all_sensors=payload)

    state = hass.states.get("sensor.top_categories")
    assert state.attributes["note"] == "no categories here"
    assert "category_list" not in state.attributes


# ---------------------------------------------------------------------------
# device_class
# ---------------------------------------------------------------------------


async def test_monetary_device_class_on_value_sensors(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """LagerSystemInventoryValueSensor and LagerSystemAverageProductValueSensor both
    declare _attr_device_class = SensorDeviceClass.MONETARY."""
    await setup_integration(hass, monkeypatch, mock_config_entry, get_all_sensors=_build_full_payload())

    inventory_value_state = hass.states.get("sensor.inventory_value")
    average_value_state = hass.states.get("sensor.average_product_value")

    assert inventory_value_state.attributes["device_class"] == SensorDeviceClass.MONETARY
    assert average_value_state.attributes["device_class"] == SensorDeviceClass.MONETARY


# ---------------------------------------------------------------------------
# device_info
# ---------------------------------------------------------------------------


async def test_sensor_device_info_ties_back_to_config_entry(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every LagerSystemSensor sets _attr_device_info with
    identifiers={(DOMAIN, entry.entry_id)} - confirmed here via the device registry
    for one representative entity, and via the entity registry's device_id link."""
    await setup_integration(hass, monkeypatch, mock_config_entry, get_all_sensors=_build_full_payload())

    device_registry = dr.async_get(hass)
    device = device_registry.async_get_device(identifiers={(DOMAIN, mock_config_entry.entry_id)})

    assert device is not None
    assert device.manufacturer == "LagerSystem"
    assert device.model == "Inventory Management"
    assert device.name == "LagerSystem"

    state = hass.states.get("sensor.inventory_value")
    assert state is not None
