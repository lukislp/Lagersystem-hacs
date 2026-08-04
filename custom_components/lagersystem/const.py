"""Constants for the LagerSystem integration."""

DOMAIN = "lagersystem"

# Configuration
CONF_HOST = "host"
CONF_API_KEY = "api_key"
CONF_VERIFY_SSL = "verify_ssl"

# Default values
DEFAULT_NAME = "LagerSystem"
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
DEFAULT_VERIFY_SSL = True

# ===== API ENDPOINTS - SENSORS =====
ENDPOINT_INVENTORY_VALUE = "/api/sensors/inventory-value"
ENDPOINT_TOTAL_PRODUCTS = "/api/sensors/total-products"
ENDPOINT_LOW_STOCK_COUNT = "/api/sensors/low-stock-count"
ENDPOINT_EXPIRY_WARNINGS = "/api/sensors/expiry-warnings"
ENDPOINT_STORAGE_UTILIZATION = "/api/sensors/storage-utilization"
ENDPOINT_DAILY_MOVEMENTS = "/api/sensors/daily-movements"
ENDPOINT_TOP_CATEGORIES = "/api/sensors/top-categories"
ENDPOINT_SENSORS_ALL = "/api/sensors/all"

# ===== API ENDPOINTS - ALERTS =====
ENDPOINT_ALERTS_SUMMARY = "/api/alerts/summary"

# ===== API ENDPOINTS - ANALYTICS =====
ENDPOINT_ANALYTICS_OVERVIEW = "/api/analytics/overview"
ENDPOINT_ANALYTICS_TRENDS = "/api/analytics/trends"
ENDPOINT_ANALYTICS_TOP_PRODUCTS = "/api/analytics/top-products"

# ===== API ENDPOINTS - DASHBOARD =====
ENDPOINT_DASHBOARD_DATA = "/api/dashboard"

# ===== API ENDPOINTS - WAREHOUSES =====
ENDPOINT_WAREHOUSES = "/api/warehouses"
ENDPOINT_WAREHOUSE_STATISTICS = "/api/warehouses/{id}/statistics"

# ===== API ENDPOINTS - ROOMS =====
ENDPOINT_ROOMS = "/api/rooms"
ENDPOINT_ROOM_PRODUCTS = "/api/rooms/{id}/products"

# ===== API ENDPOINTS - STORAGE LOCATIONS =====
ENDPOINT_STORAGE_LOCATIONS = "/api/storage-locations"
ENDPOINT_STORAGE_LOCATION_PRODUCTS = "/api/storage-locations/{id}/products"

# ===== API ENDPOINTS - USERS =====
ENDPOINT_USERS = "/api/users"
ENDPOINT_USER_STATISTICS = "/api/users/{id}/statistics"

# ===== API ENDPOINTS - NOTIFICATIONS =====
ENDPOINT_NOTIFICATIONS = "/api/notifications"
ENDPOINT_NOTIFICATIONS_UNREAD = "/api/notifications/unread"
ENDPOINT_NOTIFICATIONS_MARK_READ = "/api/notifications/{id}/mark-read"
ENDPOINT_NOTIFICATIONS_MARK_ALL_READ = "/api/notifications/mark-all-read"

# ===== API ENDPOINTS - AUDIT LOGS =====
ENDPOINT_AUDIT_LOGS = "/api/audit-logs"
ENDPOINT_AUDIT_LOGS_EXPORT = "/api/audit-logs/export"

# ===== API ENDPOINTS - MOVEMENTS =====
ENDPOINT_MOVEMENTS = "/api/movements"
ENDPOINT_MOVEMENTS_RECENT = "/api/movements/recent"

# ===== API ENDPOINTS - BATCHES =====
ENDPOINT_BATCHES = "/api/batches"
ENDPOINT_BATCHES_EXPIRING = "/api/batches/expiring"
