"""Constants for the eTilbudsavis integration."""

DOMAIN = "etilbudsavis"
PLATFORMS = ["sensor"]

API_BASE = "https://api.etilbudsavis.dk/v2/offers/search"
API_CATALOGS = "https://api.etilbudsavis.dk/v2/catalogs"
API_LOCALE = "da_DK"
API_AV = "0.3.0"

DEFAULT_RADIUS = 25000
DEFAULT_SCAN_INTERVAL = 21600  # 6 hours
DEFAULT_LIMIT = 100  # API maximum per request
CATALOG_MAX_PAGES = 5
# "paged" = printed-style catalogs, "incito" = digital catalogs (e.g. Biltema, BAUHAUS)
CATALOG_TYPES = ["paged", "incito"]

CONF_SEARCH_TERMS = "search_terms"
CONF_RADIUS = "radius"
CONF_STORES = "stores"
CONF_CANS_ONLY = "cans_only"
CONF_PRICE_PER_LITER = "price_per_liter"
CONF_PRICE_PER_KG = "price_per_kg"
CONF_MAX_OFFERS = "max_offers"
CONF_CATALOGS = "catalogs"
CONF_FEATURES = "features"
FEATURE_SEARCH = "search"
FEATURE_CATALOGS = "catalogs"

ALL_STORES = [
    "Bilka",
    "Coop 365",
    "Fakta",
    "Føtex",
    "Kvickly",
    "Lidl",
    "Meny",
    "Netto",
    "Rema1000",
    "Spar",
    "SuperBrugsen",
]

# Store names as users type them, mapped to the API's branding name
STORE_ALIASES = {
    "coop365": "365discount",
    "fakta": "365discount",  # Fakta was renamed Coop 365
}
