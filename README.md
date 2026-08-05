# LagerSystem for Home Assistant

[![CI/CD](https://github.com/lukislp/Lagersystem-hacs/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/lukislp/Lagersystem-hacs/actions/workflows/ci-cd.yml)
[![Release](https://img.shields.io/github/v/release/lukislp/Lagersystem-hacs)](https://github.com/lukislp/Lagersystem-hacs/releases)
[![License: MIT](https://img.shields.io/github/license/lukislp/Lagersystem-hacs)](LICENSE)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/lukislp/Lagersystem-hacs/main/.github/badges/coverage.json)](https://github.com/lukislp/Lagersystem-hacs/actions/workflows/ci-cd.yml)

Home Assistant custom integration for [LagerSystem](https://github.com/lukislp/Lagersystem), a
self-hosted warehouse/inventory management app. Polls the LagerSystem REST API and exposes
inventory levels, stock/expiry alerts, and warehouse statistics as sensors, binary sensors, and
action buttons.

## Installation

### HACS (recommended)

1. Open **HACS** in Home Assistant → **Integrations**
2. Menu (⋮) → **Custom repositories**
3. Add this repository URL with category **Integration**
4. Install **LagerSystem**, then restart Home Assistant
5. **Settings → Devices & Services → Add Integration → "LagerSystem"**

### Manual

Copy `custom_components/lagersystem` into your Home Assistant `config/custom_components/`
directory and restart Home Assistant.

## Configuration

Generate an API key in LagerSystem (**Profile → API Keys → Create API Key**), then enter:

| Field | Description |
|---|---|
| Host URL | e.g. `https://your-domain.com:7239` |
| API Key | the key generated above |
| Verify SSL certificate | on by default; turn off only if your server uses a self-signed certificate |

The integration polls every 30 seconds by default (configurable in `custom_components/lagersystem/__init__.py`'s `SCAN_INTERVAL`).

## Entities

All entities share one device (`LagerSystem`).

### Sensors (18)

| Entity | Unit | Description |
|---|---|---|
| Inventory Value | € | Total warehouse value |
| Total Products | count | Number of products |
| Low Stock Products | count | Products below their minimum threshold |
| Expiring Products | count | Products expiring within 7 days |
| Storage Utilization | % | Warehouse capacity in use |
| Movements Today | count | Stock movements logged today |
| Top Categories | list | Top 5 categories by value |
| Total Warehouses | count | Number of warehouses |
| Total Rooms | count | Number of rooms |
| Total Storage Locations | count | Number of storage locations |
| Total Users | count | Number of users |
| Unread Notifications | count | Unread notification count |
| Movements (Last Hour) | count | Stock movements in the last hour |
| Expiring Batches | count | Batches expiring within 7 days |
| Audit Logs (30 Days) | count | Audit log entries in the last 30 days |
| Active Users | count | Users active in the last 7 days |
| Total Warehouse Capacity | % | Aggregate storage capacity in use |
| Average Product Value | € | Average value per product |

### Binary Sensors (4)

| Entity | Device Class | Trigger |
|---|---|---|
| Low Stock Alert | problem | Any product below its minimum threshold |
| Expiry Alert | problem | Products expiring within 7 days |
| Storage Critical Alert | problem | Warehouse storage ≥ 90% full |
| High Activity Alert | running | More than 50 stock movements today |

### Buttons (7)

| Entity | Action |
|---|---|
| Mark All Notifications Read | Marks all notifications as read |
| Clear Old Notifications | Deletes notifications older than 30 days |
| Export Audit Logs | Triggers a CSV export of audit logs |
| Clean Old Audit Logs | Deletes audit log entries older than 90 days |
| Generate Analytics Report | Triggers analytics report generation |
| Refresh Analytics | Refreshes analytics data |
| Refresh Dashboard | Forces an immediate data refresh |

## Dashboard example

```yaml
type: entities
title: Warehouse Overview
entities:
  - entity: sensor.lagersystem_inventory_value
    name: Total Value
    icon: mdi:currency-eur
  - entity: sensor.lagersystem_total_products
    name: Products
    icon: mdi:package-variant
  - entity: sensor.lagersystem_storage_utilization
    name: Storage Usage
    icon: mdi:chart-donut
  - entity: sensor.lagersystem_daily_movements
    name: Today's Movements
    icon: mdi:swap-horizontal
```

```yaml
type: horizontal-stack
cards:
  - type: gauge
    entity: sensor.lagersystem_storage_utilization
    name: Storage
    min: 0
    max: 100
    severity:
      green: 0
      yellow: 75
      red: 90
    needle: true
  - type: gauge
    entity: sensor.lagersystem_inventory_value
    name: Inventory Value
    min: 0
    max: 50000
    unit: €
```

## Automation example

```yaml
automation:
  - alias: "Warehouse: Low Stock Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.lagersystem_low_stock_alert
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Low Stock Alert"
          message: "{{ states('sensor.lagersystem_low_stock') }} products need restocking"
          data:
            priority: high
            tag: low_stock
```

## Requirements

- Home Assistant 2024.1 or newer
- A running LagerSystem instance with API access enabled

## Known limitations

- The integration issues one batch request per poll cycle against a fixed set of endpoints;
  it does not (yet) cover every LagerSystem API area — search, per-item CRUD, and user
  administration are intentionally out of scope for a dashboard-focused integration.
- Timer/session state depends on the poll interval; there is no push/webhook channel yet.

## License

[MIT](LICENSE).
