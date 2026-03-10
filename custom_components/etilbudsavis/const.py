"""Constants for the eTilbudsavis integration."""

DOMAIN = "etilbudsavis"
PLATFORMS = ["sensor"]

API_BASE = "https://api.etilbudsavis.dk/v2/offers/search"
API_LOCALE = "da_DK"
API_AV = "0.3.0"

DEFAULT_RADIUS = 25000
DEFAULT_SCAN_INTERVAL = 21600  # 6 hours
DEFAULT_LIMIT = 24

CONF_SEARCH_TERMS = "search_terms"
CONF_RADIUS = "radius"
CONF_STORES = "stores"
CONF_CANS_ONLY = "cans_only"
CONF_PRICE_PER_LITER = "price_per_liter"
CONF_MAX_OFFERS = "max_offers"

ALL_STORES = [
    "Bilka",
    "Coop 365",
    "fakta",
    "Føtex",
    "Kvickly",
    "Lidl",
    "Meny",
    "Netto",
    "Rema 1000",
    "Spar",
    "SuperBrugsen",
]
