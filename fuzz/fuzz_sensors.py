"""Atheris fuzz harness for the sensor entities' view of the coordinator payload.

Contract under test: whatever GET /api/sensors returned (any JSON shape, not just the
documented {"success": true, "data": [...]}), every sensor's native_value / is_on and
extra_state_attributes must degrade to their defaults instead of raising - an exception
in a state property takes the entity out of Home Assistant's state machine.

Run locally (Linux, needs the atheris wheel):
    pip install --require-hashes -r requirements_test.txt -r requirements_fuzz.txt
    PYTHONPATH=. python fuzz/fuzz_sensors.py -max_total_time=60
CI runs the same harness for a short, fixed time budget (see .github/workflows/ci-cd.yml).
"""

from __future__ import annotations

import inspect
import json
import sys
from types import SimpleNamespace
from typing import Any

import atheris

from custom_components.lagersystem import binary_sensor as binary_sensor_module
from custom_components.lagersystem import sensor as sensor_module
from custom_components.lagersystem.binary_sensor import LagerSystemBinarySensor
from custom_components.lagersystem.sensor import LagerSystemSensor


def _subclasses(module: Any, base: type) -> tuple[type, ...]:
    return tuple(
        cls
        for _, cls in inspect.getmembers(module, inspect.isclass)
        if issubclass(cls, base) and cls is not base
    )


SENSOR_CLASSES = _subclasses(sensor_module, LagerSystemSensor)
BINARY_SENSOR_CLASSES = _subclasses(binary_sensor_module, LagerSystemBinarySensor)
ENTITY_IDS = (
    "sensor.inventory_total_value",
    "sensor.inventory_total_products",
    "sensor.inventory_low_stock_count",
    "sensor.inventory_expiry_warnings",
)


def _value(fdp: atheris.FuzzedDataProvider, depth: int = 0) -> Any:
    kind = fdp.ConsumeIntInRange(0, 6)
    if kind == 0:
        return None
    if kind == 1:
        return fdp.ConsumeBool()
    if kind == 2:
        return fdp.ConsumeInt(4)
    if kind == 3 or depth > 2:
        return fdp.ConsumeUnicodeNoSurrogates(16)
    if kind == 4:
        return [_value(fdp, depth + 1) for _ in range(fdp.ConsumeIntInRange(0, 3))]
    if kind == 5:
        return {
            "entityId": ENTITY_IDS[fdp.ConsumeIntInRange(0, len(ENTITY_IDS) - 1)],
            "value": _value(fdp, depth + 1),
            "attributes": _value(fdp, depth + 1),
        }
    return {fdp.ConsumeUnicodeNoSurrogates(8): _value(fdp, depth + 1)}


def _payload(fdp: atheris.FuzzedDataProvider) -> Any:
    if fdp.ConsumeBool():
        try:
            return json.loads(fdp.ConsumeUnicodeNoSurrogates(256))
        except ValueError:
            return None
    return {
        "success": _value(fdp),
        "data": [_value(fdp) for _ in range(fdp.ConsumeIntInRange(0, 4))]
        if fdp.ConsumeBool()
        else _value(fdp),
    }


def test_one_input(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)
    coordinator = SimpleNamespace(data=_payload(fdp))
    for cls in SENSOR_CLASSES:
        # Bypass CoordinatorEntity.__init__ (needs a live hass/coordinator); the state
        # properties only ever read self.coordinator.data.
        entity = cls.__new__(cls)
        entity.coordinator = coordinator
        entity.native_value  # noqa: B018 - property access is the operation under test
        entity.extra_state_attributes  # noqa: B018
    for cls in BINARY_SENSOR_CLASSES:
        entity = cls.__new__(cls)
        entity.coordinator = coordinator
        entity.is_on  # noqa: B018
        entity.extra_state_attributes  # noqa: B018


if __name__ == "__main__":
    atheris.instrument_all()
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()
