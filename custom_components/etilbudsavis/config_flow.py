"""Config flow for eTilbudsavis."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    ALL_STORES,
    CONF_CANS_ONLY,
    CONF_MAX_OFFERS,
    CONF_PRICE_PER_LITER,
    CONF_RADIUS,
    CONF_SEARCH_TERMS,
    CONF_STORES,
    DEFAULT_RADIUS,
    DOMAIN,
)


def _terms_schema(defaults: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_SEARCH_TERMS,
                default=defaults.get(CONF_SEARCH_TERMS, ""),
            ): str,
        }
    )


def _parse_terms(raw: str) -> list[str]:
    """Parse comma-separated search terms."""
    return [t.strip() for t in raw.split(",") if t.strip()]


class EtilbudsavisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict = {}

    async def async_step_user(self, user_input=None):
        """Step 1: search terms."""
        errors = {}
        if user_input is not None:
            terms = _parse_terms(user_input[CONF_SEARCH_TERMS])
            if not terms:
                errors[CONF_SEARCH_TERMS] = "no_terms"
            else:
                self._data[CONF_SEARCH_TERMS] = terms
                return await self.async_step_options()

        return self.async_show_form(
            step_id="user",
            data_schema=_terms_schema({}),
            description_placeholders={
                "example": "pepsi max, faxe kondi lemonade, tuborg"
            },
            errors=errors,
        )

    async def async_step_options(self, user_input=None):
        """Step 2: options."""
        errors = {}
        if user_input is not None:
            stores_raw = user_input.get(CONF_STORES, "")
            stores = (
                [s.strip() for s in stores_raw.split(",") if s.strip()]
                if isinstance(stores_raw, str)
                else stores_raw
            )
            self._data.update(
                {
                    CONF_STORES: stores,
                    CONF_RADIUS: user_input[CONF_RADIUS],
                    CONF_CANS_ONLY: user_input[CONF_CANS_ONLY],
                    CONF_PRICE_PER_LITER: user_input[CONF_PRICE_PER_LITER],
                    CONF_MAX_OFFERS: user_input[CONF_MAX_OFFERS],
                }
            )
            title = ", ".join(self._data[CONF_SEARCH_TERMS][:2])
            if len(self._data[CONF_SEARCH_TERMS]) > 2:
                title += f" +{len(self._data[CONF_SEARCH_TERMS]) - 2}"
            return self.async_create_entry(title=title, data=self._data)

        stores_default = ", ".join(ALL_STORES)
        schema = vol.Schema(
            {
                vol.Optional(CONF_STORES, default=stores_default): str,
                vol.Optional(CONF_RADIUS, default=DEFAULT_RADIUS): int,
                vol.Optional(CONF_CANS_ONLY, default=False): bool,
                vol.Optional(CONF_PRICE_PER_LITER, default=False): bool,
                vol.Optional(CONF_MAX_OFFERS, default=5): int,
            }
        )

        return self.async_show_form(
            step_id="options",
            data_schema=schema,
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
            terms = _parse_terms(user_input[CONF_SEARCH_TERMS])
            if not terms:
                errors[CONF_SEARCH_TERMS] = "no_terms"
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
                        CONF_MAX_OFFERS: user_input[CONF_MAX_OFFERS],
                    },
                )

        terms_default = ", ".join(existing.get(CONF_SEARCH_TERMS, []))
        stores_default = ", ".join(existing.get(CONF_STORES, ALL_STORES))

        schema = vol.Schema(
            {
                vol.Required(CONF_SEARCH_TERMS, default=terms_default): str,
                vol.Optional(CONF_STORES, default=stores_default): str,
                vol.Optional(CONF_RADIUS, default=existing.get(CONF_RADIUS, DEFAULT_RADIUS)): int,
                vol.Optional(CONF_CANS_ONLY, default=existing.get(CONF_CANS_ONLY, False)): bool,
                vol.Optional(CONF_PRICE_PER_LITER, default=existing.get(CONF_PRICE_PER_LITER, False)): bool,
                vol.Optional(CONF_MAX_OFFERS, default=existing.get(CONF_MAX_OFFERS, 5)): int,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
