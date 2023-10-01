"""The GroupAlarm.com component."""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .connector import GroupAlarmData
from .const import (
    DEFAULT_SCAN_INTERVAL,
    GROUPALARM_STATE_SERVICE,
    DOMAIN,
    GROUPALARM_COORDINATOR,
    GROUPALARM_DATA,
    GROUPALARM_NAME,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SELECT, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up GroupAlarm as config entry."""

    # Load values from settings
    access_token = entry.data[CONF_ACCESS_TOKEN]
    site_name = entry.data[CONF_NAME]

    groupalarm_data = GroupAlarmData(hass, access_token)

    # Update data initially
    await groupalarm_data.async_update()
    if not groupalarm_data.success:
        raise ConfigEntryNotReady()

    # Coordinator checks for new updates
    groupalarm_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"GroupAlarm Coordinator for {site_name}",
        update_method=groupalarm_data.async_update,
        update_interval=DEFAULT_SCAN_INTERVAL,
    )

    # Save the data
    groupalarm_hass_data = hass.data.setdefault(DOMAIN, {})
    groupalarm_hass_data[entry.entry_id] = {
        GROUPALARM_DATA: groupalarm_data,
        GROUPALARM_COORDINATOR: groupalarm_coordinator,
        GROUPALARM_NAME: site_name,
    }

    # Fetch initial data so we have data when entities subscribe
    await groupalarm_coordinator.async_refresh()
    if not groupalarm_data.success:
        raise ConfigEntryNotReady()

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        new = {**config_entry.data}
        # new[CONF_UPDATE_INTERVAL] = 24
        config_entry.data = {**new}
        config_entry.version = 2

    _LOGGER.info("Migration to version %s successful", config_entry.version)
    return True


async def async_update(self):
    """Async wrapper for update method."""
    return await self._hass.async_add_executor_job(self._update)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    hass.services.async_remove(DOMAIN, GROUPALARM_STATE_SERVICE)

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok
