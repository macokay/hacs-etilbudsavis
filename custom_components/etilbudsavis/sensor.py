"""Sensor platform for eTilbudsavis."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EtilbudsavisCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up eTilbudsavis sensors."""
    coordinator: EtilbudsavisCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        EtilbudsavisSensor(coordinator, term)
        for term in coordinator.search_terms
    ]
    async_add_entities(entities)


class EtilbudsavisSensor(CoordinatorEntity, SensorEntity):
    """Sensor for a single search term."""

    def __init__(self, coordinator: EtilbudsavisCoordinator, term: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._term = term
        slug = term.lower().replace(" ", "_")
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{slug}"
        self._attr_name = f"Tilbud - {term.title()}"
        self._attr_icon = "mdi:tag-outline"

    @property
    def native_value(self) -> int:
        """Return number of offers found."""
        offers = (self.coordinator.data or {}).get(self._term, [])
        return len(offers)

    @property
    def native_unit_of_measurement(self) -> str:
        return "tilbud"

    @property
    def extra_state_attributes(self) -> dict:
        """Return offers as attributes."""
        offers = (self.coordinator.data or {}).get(self._term, [])
        attrs: dict = {"search_term": self._term, "offers": offers}

        if offers:
            best = None
            for o in offers:
                ppl = o.get("price_per_liter")
                ppk = o.get("price_per_kg")
                price = o.get("price")
                val = ppl if ppl is not None else (ppk if ppk is not None else price)
                if val is not None and (best is None or val < best["_val"]):
                    best = {**o, "_val": val}
            if best:
                best.pop("_val", None)
                attrs["best_offer"] = best

        return attrs

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success
