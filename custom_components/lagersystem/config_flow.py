"""Config flow for LagerSystem integration."""
import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LagerSystemAPI
from .const import CONF_VERIFY_SSL, DEFAULT_NAME, DEFAULT_VERIFY_SSL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class LagerSystemConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LagerSystem."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            api_key = user_input[CONF_API_KEY]
            verify_ssl = user_input[CONF_VERIFY_SSL]

            session = async_get_clientsession(self.hass)
            api = LagerSystemAPI(host, api_key, session, verify_ssl)

            try:
                connected = await api.test_connection()
            except Exception:
                # Only the API call is guarded here - _abort_if_unique_id_configured()
                # below raises AbortFlow (an Exception subclass) as its normal control
                # flow, and a try around it would misreport a legitimate abort as this
                # generic "unknown" error instead of letting it reach the flow manager.
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                if connected:
                    await self.async_set_unique_id(f"{host}_apikey")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=DEFAULT_NAME,
                        data={
                            CONF_HOST: host,
                            CONF_API_KEY: api_key,
                            CONF_VERIFY_SSL: verify_ssl,
                        },
                    )
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default="https://your-domain.com"): cv.string,
                    vol.Required(CONF_API_KEY): cv.string,
                    vol.Required(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): cv.boolean,
                }
            ),
            errors=errors,
        )
