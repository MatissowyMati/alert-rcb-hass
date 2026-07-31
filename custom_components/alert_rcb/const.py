"""Constants for the RSO integration."""

from typing import Final

DOMAIN: Final = "alert_rcb"
PLATFORMS: Final = ["binary_sensor", "button", "calendar", "event", "sensor"]

API_BASE_URL: Final = "https://komunikaty.tvp.pl"
API_TIMEOUT_SECONDS: Final = 20
ATTRIBUTION: Final = "Data provided by Regionalny System Ostrzegania (TVP)"

CONF_PROVINCE: Final = "province"
CONF_CATEGORY: Final = "category"
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_NOTIFICATION_MODE: Final = "notification_mode"

DEFAULT_PROVINCE: Final = "wszystkie"
DEFAULT_CATEGORY: Final = "wszystkie"
DEFAULT_SCAN_INTERVAL: Final = 1
DEFAULT_NOTIFICATION_MODE: Final = "critical"
MIN_SCAN_INTERVAL: Final = 1
MAX_SCAN_INTERVAL: Final = 1440

NOTIFICATION_MODES: Final = ["none", "critical", "all"]
EVENT_NEW_ALERT: Final = "alert_rcb_new_alert"
EVENT_UPDATED_ALERT: Final = "alert_rcb_updated_alert"
SIGNAL_ALERT: Final = f"{DOMAIN}_alert"

PROVINCES: Final = {
    "wszystkie": "Cała Polska",
    "dolnoslaskie": "Dolnośląskie",
    "kujawsko-pomorskie": "Kujawsko-Pomorskie",
    "lubelskie": "Lubelskie",
    "lubuskie": "Lubuskie",
    "lodzkie": "Łódzkie",
    "malopolskie": "Małopolskie",
    "mazowieckie": "Mazowieckie",
    "opolskie": "Opolskie",
    "podkarpackie": "Podkarpackie",
    "podlaskie": "Podlaskie",
    "pomorskie": "Pomorskie",
    "slaskie": "Śląskie",
    "swietokrzyskie": "Świętokrzyskie",
    "warminsko-mazurskie": "Warmińsko-Mazurskie",
    "wielkopolskie": "Wielkopolskie",
    "zachodniopomorskie": "Zachodniopomorskie",
}

CATEGORIES: Final = {
    "wszystkie": "Wszystkie",
    "ogolne": "Ogólne",
    "meteorologiczne": "Meteorologiczne",
    "hydrologiczne": "Hydrologiczne",
    "informacje-drogowe": "Informacje drogowe",
    "stany-wod": "Stany wód",
}
