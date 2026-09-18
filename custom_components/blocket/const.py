"""Constants for the Blocket integration."""

DOMAIN = "blocket"

CONF_SEARCH_URL = "search_url"
CONF_WATCH_NAME = "watch_name"
CONF_POLL_INTERVAL = "poll_interval"
CONF_INPUT_METHOD = "input_method"
CONF_MARKETPLACE_TYPE = "marketplace_type"
CONF_REGION = "region"
CONF_CATEGORY = "category"
CONF_SORT_ORDER = "sort_order"

DEFAULT_POLL_INTERVAL = 10
MIN_POLL_INTERVAL = 5
MAX_POLL_INTERVAL = 1440

INPUT_METHOD_URL = "url"
INPUT_METHOD_BUILDER = "builder"

MARKETPLACE_MOBILITY = "mobility"
MARKETPLACE_RECOMMERCE = "recommerce"

REGIONS = {
	"all": "Hela Sverige",
	"0.300001": "Stockholm",
	"0.300012": "Skåne",
	"0.300013": "Västra Götaland",
	"0.300002": "Uppsala",
	"0.300003": "Södermanland",
	"0.300004": "Östergötland",
	"0.300005": "Jönköping",
	"0.300006": "Kronoberg",
	"0.300007": "Kalmar",
	"0.300008": "Gotland",
	"0.300009": "Blekinge",
	"0.300010": "Halland",
	"0.300011": "Värmland",
	"0.300014": "Örebro",
	"0.300015": "Västmanland",
	"0.300016": "Dalarna",
	"0.300017": "Gävleborg",
	"0.300018": "Västernorrland",
	"0.300019": "Jämtland",
	"0.300020": "Västerbotten",
	"0.300021": "Norrbotten",
}

RECOMMERCE_CATEGORIES = {
	"all": "Alla kategorier",
	"0.93": "Elektronik",
	"0.78": "Möbler & Heminredning",
	"0.62": "Kläder & Skor",
	"0.40": "Fritid & Hobby",
	"0.89": "Hem & Trädgård",
	"0.24": "Barn & Baby",
	"0.10": "Verktyg & Maskiner",
	"0.94": "Musikutrustning",
	"0.83": "Sport & Fritid",
	"0.52": "Böcker & Studentlitteratur",
}

SORT_ORDERS = {
	"PUBLISHED_DESC": "Nyast först",
	"PUBLISHED_ASC": "Äldst först",
	"PRICE_ASC": "Lägsta pris först",
	"PRICE_DESC": "Högsta pris först",
}

EVENT_NEW_LISTING = "blocket_new_listing"

USER_AGENT = "HomeAssistant-Blocket-unofficial/0.2.0 (https://github.com/Vortitron/ha-blocket)"
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
