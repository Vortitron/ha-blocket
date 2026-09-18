"""Constants for the Blocket integration."""

DOMAIN = "blocket"

CONF_SEARCH_URL = "search_url"
CONF_WATCH_NAME = "watch_name"
CONF_POLL_INTERVAL = "poll_interval"

DEFAULT_POLL_INTERVAL = 10
MIN_POLL_INTERVAL = 5
MAX_POLL_INTERVAL = 1440

EVENT_NEW_LISTING = "blocket_new_listing"

USER_AGENT = "HomeAssistant-Blocket-unofficial/0.1.0 (https://github.com/Vortitron/ha-blocket)"
REQUEST_TIMEOUT = 30

ATTR_SOURCE = "source"
ATTR_WATCH_ID = "watch_id"
ATTR_WATCH_NAME = "watch_name"
ATTR_LISTING_ID = "listing_id"
ATTR_TITLE = "title"
ATTR_PRICE = "price"
ATTR_CURRENCY = "currency"
ATTR_URL = "url"
ATTR_IMAGE_URL = "image_url"
ATTR_LOCATION = "location"
ATTR_DISCOVERED_AT = "discovered_at"
