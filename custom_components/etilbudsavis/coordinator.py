"""DataUpdateCoordinator for eTilbudsavis."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_AV,
    API_BASE,
    API_LOCALE,
    CONF_CANS_ONLY,
    CONF_MAX_OFFERS,
    CONF_PRICE_PER_KG,
    CONF_PRICE_PER_LITER,
    CONF_RADIUS,
    CONF_SEARCH_TERMS,
    CONF_STORES,
    DEFAULT_LIMIT,
    DEFAULT_RADIUS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

CAN_KEYWORDS = ["dåse", "dåser", "can", "cans"]
UNIT_TO_LITER = {"cl": 0.01, "ml": 0.001, "l": 1.0, "dl": 0.1}
UNIT_TO_KG = {"g": 0.001, "kg": 1.0, "hg": 0.1}


def _extract_liter(offer: dict) -> float | None:
    """Try to extract total liters from quantity fields."""
    q = offer.get("quantity", {})
    if not q:
        return None
    size = (q.get("size") or {}).get("from", 0)
    pieces = (q.get("pieces") or {}).get("from", 1)
    unit = ((q.get("unit") or {}).get("symbol") or "").lower()
    factor = UNIT_TO_LITER.get(unit)
    if factor and size and pieces:
        return size * pieces * factor
    return None


def _extract_kg(offer: dict) -> float | None:
    """Try to extract total kilograms from quantity fields."""
    q = offer.get("quantity", {})
    if not q:
        return None
    size = (q.get("size") or {}).get("from", 0)
    pieces = (q.get("pieces") or {}).get("from", 1)
    unit = ((q.get("unit") or {}).get("symbol") or "").lower()
    factor = UNIT_TO_KG.get(unit)
    if factor and size and pieces:
        return size * pieces * factor
    return None


def _parse_offers(raw: list, stores: list, cans_only: bool, price_per_liter: bool, price_per_kg: bool, max_offers: int) -> list:
    """Filter and format offers from API response."""
    stores_lower = [s.lower() for s in stores] if stores else []
    results = []

    for offer in raw:
        if len(results) >= max_offers:
            break

        branding = offer.get("branding") or {}
        store_name = branding.get("name", "")

        if stores_lower and store_name.lower() not in stores_lower:
            continue

        if cans_only:
            heading = (offer.get("heading") or "").lower()
            desc = (offer.get("description") or "").lower()
            combined = heading + " " + desc
            if not any(kw in combined for kw in CAN_KEYWORDS):
                continue

        pricing = offer.get("pricing") or {}
        price = pricing.get("price")
        if not price:
            continue

        entry = {
            "store": store_name,
            "heading": offer.get("heading", ""),
            "description": offer.get("description", ""),
            "price": round(float(price), 2),
            "currency": pricing.get("currency", "DKK"),
            "run_from": offer.get("run_from", ""),
            "run_till": offer.get("run_till", ""),
            "catalog_page": offer.get("catalog_page"),
        }

        if price_per_liter:
            liters = _extract_liter(offer)
            if liters and liters > 0:
                entry["price_per_liter"] = round(float(price) / liters, 2)
                entry["total_liters"] = round(liters, 2)

        if price_per_kg:
            kg = _extract_kg(offer)
            if kg and kg > 0:
                entry["price_per_kg"] = round(float(price) / kg, 2)
                entry["total_kg"] = round(kg, 2)

        results.append(entry)

    return results


class EtilbudsavisCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch all search term offers."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        lat = hass.config.latitude
        lon = hass.config.longitude

        options = {**entry.data, **entry.options}
        self.search_terms: list[str] = options.get(CONF_SEARCH_TERMS, [])
        self.radius: int = options.get(CONF_RADIUS, DEFAULT_RADIUS)
        self.stores: list[str] = options.get(CONF_STORES, [])
        self.cans_only: bool = options.get(CONF_CANS_ONLY, False)
        self.price_per_liter: bool = options.get(CONF_PRICE_PER_LITER, False)
        self.price_per_kg: bool = options.get(CONF_PRICE_PER_KG, False)
        self.max_offers: int = options.get(CONF_MAX_OFFERS, 5)
        self._lat = lat
        self._lon = lon

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, list]:
        """Fetch data for all search terms."""
        results = {}
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_term(session, term)
                for term in self.search_terms
            ]
            fetched = await asyncio.gather(*tasks, return_exceptions=True)

        for term, data in zip(self.search_terms, fetched):
            if isinstance(data, Exception):
                _LOGGER.warning("Failed to fetch offers for '%s': %s", term, data)
                results[term] = []
            else:
                results[term] = _parse_offers(
                    data,
                    self.stores,
                    self.cans_only,
                    self.price_per_liter,
                    self.price_per_kg,
                    self.max_offers,
                )
        return results

    async def _fetch_term(self, session: aiohttp.ClientSession, term: str) -> list:
        """Fetch offers for a single search term."""
        params = {
            "r_lat": self._lat,
            "r_lng": self._lon,
            "r_radius": self.radius,
            "r_locale": API_LOCALE,
            "api_av": API_AV,
            "query": term,
            "offset": 0,
            "limit": DEFAULT_LIMIT,
        }
        try:
            async with session.get(API_BASE, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"API returned {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Request failed: {err}") from err
