"""Sensor for GroupAlarm 24/7 service."""

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from homeassistant.helpers.device_registry import DeviceInfo

from .const import (
    DEFAULT_SHORT_NAME,
    DEFAULT_NAME,
    DOMAIN,
    GROUPALARM_COORDINATOR,
    GROUPALARM_DATA,
    GROUPALARM_NAME,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigType, async_add_entities
) -> None:
    """Set up the GroupAlarm sensor platform."""
    hass_data = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.debug("Sensor async_setup_entry")
    async_add_entities(
        [
            GroupAlarmAlarmStartSensor(hass_data),
            GroupAlarmAlarmEndSensor(hass_data),
            GroupAlarmOrganizationSensor(hass_data),
            GroupAlarmEventSensor(hass_data),
            GroupAlarmMessageSensor(hass_data),
            GroupAlarmUserAlarmedSensor(hass_data),
            GroupAlarmUserFeedbackSensor(hass_data)      
         ],
        False,
    )

class GroupAlarmAbstractSensor(SensorEntity):
    """Implementation of a GroupAlarm sensor."""

    def __init__(self, hass_data):
        """Initialize the sensor."""
        self._connector = hass_data[GROUPALARM_DATA]
        self._coordinator = hass_data[GROUPALARM_COORDINATOR]

        self._unique_id = f"{DOMAIN}_{hass_data[GROUPALARM_NAME]}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._connector.get_alarm_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, "TODO")},
            name=DEFAULT_NAME,
            manufacturer=DEFAULT_SHORT_NAME,
        )

    async def async_added_to_hass(self) -> None:
        """Set up a listener and load data."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Schedule a custom update via the common entity update service."""
        await self._coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False

    @property
    def available(self):
        """Return if state is available."""
        return self._connector.success and self._connector.latest_update is not None

class GroupAlarmOrganizationSensor(GroupAlarmAbstractSensor):
    _attr_name = "Organization"
    _attr_icon = "mdi:account-group"

    def __init__(self, hass_data):
        super().__init__(hass_data)
        self._attr_unique_id = f"{self._attr_unique_id}_organization"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._connector.get_alarm_organization()

class GroupAlarmAlarmStartSensor(GroupAlarmAbstractSensor):
    _attr_name = "Start"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:calendar-start"
    
    def __init__(self, hass_data):
        super().__init__(hass_data)
        self._attr_unique_id = f"{self._attr_unique_id}_start"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._connector.get_alarm_start()

class GroupAlarmAlarmEndSensor(GroupAlarmAbstractSensor):
    _attr_name = "End"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:calendar-end"
    
    def __init__(self, hass_data):
        super().__init__(hass_data)
        self._attr_unique_id = f"{self._attr_unique_id}_end"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._connector.get_alarm_end()

class GroupAlarmUserAlarmedSensor(GroupAlarmAbstractSensor):
    _attr_name = "User is alarmed"
    _attr_icon = "mdi:account-alert"
    def __init__(self, hass_data):
        super().__init__(hass_data)
        self._attr_unique_id = f"{self._attr_unique_id}_user_alarmed"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._connector.get_alarm_useralarmed()

class GroupAlarmUserFeedbackSensor(GroupAlarmAbstractSensor):
    _attr_name = "Feedback"
    _attr_icon = "mdi:account-badge"
    def __init__(self, hass_data):
        super().__init__(hass_data)
        self._attr_unique_id = f"{self._attr_unique_id}_user_feedback"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._connector.get_alarm_feedback()

class GroupAlarmMessageSensor(GroupAlarmAbstractSensor):
    _attr_name = "Message"
    _attr_icon = "mdi:card-text"
    def __init__(self, hass_data):
        super().__init__(hass_data)
        self._attr_unique_id = f"{self._attr_unique_id}_message"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._connector.get_alarm_message()

class GroupAlarmEventSensor(GroupAlarmAbstractSensor):
    _attr_name = "Event"
    _attr_icon = "mdi:calendar-text"
    def __init__(self, hass_data):
        super().__init__(hass_data)
        self._attr_unique_id = f"{self._attr_unique_id}_event"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._connector.get_alarm_event()