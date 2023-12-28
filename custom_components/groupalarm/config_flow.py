"""Config flow for GroupAlarm 24/7 integration."""

import logging

import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_NAME

from .connector import GroupAlarmData
from .const import (
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    api_key = data[CONF_ACCESS_TOKEN]

    groupalarm_data = GroupAlarmData(hass, api_key)
    await groupalarm_data.async_update()
    if not groupalarm_data.success:
        raise CannotConnect()
    return {"unique_id": groupalarm_data.get_user()["email"]}


class GroupAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GroupAlarm integration."""

    VERSION = 1
    MINOR_VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                unique_id = info["unique_id"]
                user_input[CONF_NAME] = unique_id
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME].title(), data=user_input
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ACCESS_TOKEN, default=""): str,
            },
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
