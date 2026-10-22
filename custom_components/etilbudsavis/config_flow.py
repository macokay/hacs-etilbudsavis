"""Config flow for eTilbudsavis."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import (
    ALL_STORES,
    CONF_CANS_ONLY,
    CONF_CATALOGS,
    CONF_FEATURES,
    CONF_MAX_OFFERS,
    CONF_PRICE_PER_KG,
    CONF_PRICE_PER_LITER,
    CONF_RADIUS,
    CONF_SEARCH_TERMS,
    CONF_STORES,
    DEFAULT_RADIUS,
    DOMAIN,
    FEATURE_CATALOGS,
    FEATURE_SEARCH,
)
from .coordinator import _normalize_store, fetch_catalogs

# Store names are checked against every catalog in Denmark, not just the radius.
CATALOG_CHECK_RADIUS = 500000

FEATURE_SELECTOR = selector.SelectSelector(
    selector.SelectSelectorConfig(
        options=[FEATURE_SEARCH, FEATURE_CATALOGS],
        multiple=True,
        translation_key="features",
        mode=selector.SelectSelectorMode.LIST,
    )
)


def _split_csv(raw: str) -> list[str]:
    """Split a comma-separated string into trimmed, non-empty items."""
    return [t.strip() for t in raw.split(",") if t.strip()]


def _title(terms: list[str], stores: list[str]) -> str:
    """Build the entry title from the first two search terms or stores."""
    items = terms or stores
    title = ", ".join(items[:2])
    if len(items) > 2:
        title += f" +{len(items) - 2}"
    return title


class EtilbudsavisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict = {}
        self._features: list[str] = []

    async def async_step_user(self, user_input=None):
        """Step 1: choose what to follow."""
        errors = {}
        if user_input is not None:
            features = user_input[CONF_FEATURES]
            if not features:
                errors["base"] = "no_feature"
            else:
                self._features = features
                if FEATURE_SEARCH in features:
                    return await self.async_step_search()
                return await self.async_step_catalogs()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_FEATURES, default=[FEATURE_SEARCH]
                    ): FEATURE_SELECTOR,
                }
            ),
            errors=errors,
        )

    async def async_step_search(self, user_input=None):
        """Step 2a: search terms."""
        errors = {}
        if user_input is not None:
            terms = _split_csv(user_input[CONF_SEARCH_TERMS])
            if not terms:
                errors[CONF_SEARCH_TERMS] = "no_terms"
            else:
                self._data[CONF_SEARCH_TERMS] = terms
                if FEATURE_CATALOGS in self._features:
                    return await self.async_step_catalogs()
                return await self.async_step_options()

        return self.async_show_form(
            step_id="search",
            data_schema=vol.Schema({vol.Required(CONF_SEARCH_TERMS, default=""): str}),
            description_placeholders={
                "example": "pepsi max, faxe kondi lemonade, tuborg"
            },
            errors=errors,
        )

    async def async_step_catalogs(self, user_input=None):
        """Step 2b: stores whose catalogs to follow."""
        errors = {}
        if user_input is not None:
            stores = _split_csv(user_input[CONF_CATALOGS])
            if not stores:
                errors[CONF_CATALOGS] = "no_stores"
            else:
                try:
                    known = await self._known_stores()
                except UpdateFailed:
                    errors["base"] = "cannot_connect"
                else:
                    if any(_normalize_store(s) not in known for s in stores):
                        errors[CONF_CATALOGS] = "unknown_store"
                    else:
                        self._data[CONF_CATALOGS] = stores
                        return await self.async_step_options()

        return self.async_show_form(
            step_id="catalogs",
            data_schema=vol.Schema({vol.Required(CONF_CATALOGS, default=""): str}),
            errors=errors,
        )

    async def _known_stores(self) -> set[str]:
        """Normalized names of every store that publishes a catalog."""
        session = async_get_clientsession(self.hass)
        catalogs = await fetch_catalogs(
            session,
            self.hass.config.latitude,
            self.hass.config.longitude,
            CATALOG_CHECK_RADIUS,
        )
        return {_normalize_store(c["branding"]["name"]) for c in catalogs}

    async def async_step_options(self, user_input=None):
        """Step 3: options. Offer settings only apply when searching."""
        errors = {}
        if user_input is not None:
            if CONF_STORES in user_input:
                user_input[CONF_STORES] = _split_csv(user_input[CONF_STORES])
            self._data.setdefault(CONF_SEARCH_TERMS, [])
            self._data.setdefault(CONF_CATALOGS, [])
            self._data.update(user_input)
            title = _title(self._data[CONF_SEARCH_TERMS], self._data[CONF_CATALOGS])
            return self.async_create_entry(title=title, data=self._data)

        schema: dict = {vol.Optional(CONF_RADIUS, default=DEFAULT_RADIUS): int}
        if FEATURE_SEARCH in self._features:
            schema.update(
                {
                    vol.Optional(CONF_STORES, default=", ".join(ALL_STORES)): str,
                    vol.Optional(CONF_CANS_ONLY, default=False): bool,
                    vol.Optional(CONF_PRICE_PER_LITER, default=False): bool,
                    vol.Optional(CONF_PRICE_PER_KG, default=False): bool,
                    vol.Optional(CONF_MAX_OFFERS, default=5): int,
                }
            )

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema(schema),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return EtilbudsavisOptionsFlow(config_entry)


class EtilbudsavisOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow (edit after setup)."""

    def __init__(self, config_entry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        existing = {**self._config_entry.data, **self._config_entry.options}

        if user_input is not None:
            terms = _split_csv(user_input[CONF_SEARCH_TERMS])
            catalogs = _split_csv(user_input[CONF_CATALOGS])
            if not terms and not catalogs:
                errors["base"] = "no_feature"
            else:
                stores_raw = user_input.get(CONF_STORES, "")
                stores = (
                    [s.strip() for s in stores_raw.split(",") if s.strip()]
                    if isinstance(stores_raw, str)
                    else stores_raw
                )
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_SEARCH_TERMS: terms,
                        CONF_STORES: stores,
                        CONF_RADIUS: user_input[CONF_RADIUS],
                        CONF_CANS_ONLY: user_input[CONF_CANS_ONLY],
                        CONF_PRICE_PER_LITER: user_input[CONF_PRICE_PER_LITER],
                        CONF_PRICE_PER_KG: user_input[CONF_PRICE_PER_KG],
                        CONF_MAX_OFFERS: user_input[CONF_MAX_OFFERS],
                        CONF_CATALOGS: catalogs,
                    },
                )

        terms_default = ", ".join(existing.get(CONF_SEARCH_TERMS, []))
        stores_default = ", ".join(existing.get(CONF_STORES, ALL_STORES))
        catalogs_default = ", ".join(existing.get(CONF_CATALOGS, []))

        schema = vol.Schema(
            {
                vol.Optional(CONF_SEARCH_TERMS, default=terms_default): str,
                vol.Optional(CONF_CATALOGS, default=catalogs_default): str,
                vol.Optional(CONF_STORES, default=stores_default): str,
                vol.Optional(
                    CONF_RADIUS, default=existing.get(CONF_RADIUS, DEFAULT_RADIUS)
                ): int,
                vol.Optional(
                    CONF_CANS_ONLY, default=existing.get(CONF_CANS_ONLY, False)
                ): bool,
                vol.Optional(
                    CONF_PRICE_PER_LITER,
                    default=existing.get(CONF_PRICE_PER_LITER, False),
                ): bool,
                vol.Optional(
                    CONF_PRICE_PER_KG, default=existing.get(CONF_PRICE_PER_KG, False)
                ): bool,
                vol.Optional(
                    CONF_MAX_OFFERS, default=existing.get(CONF_MAX_OFFERS, 5)
                ): int,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
