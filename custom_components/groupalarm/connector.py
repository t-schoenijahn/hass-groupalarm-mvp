"""Connector Class for GroupAlarm Data."""

from datetime import datetime
import logging
import json
import requests

from homeassistant.const import STATE_UNKNOWN
from .const import DEFAULT_TIMEOUT, GROUPALARM_STATUS_URL, GROUPALARM_URL

_LOGGER = logging.getLogger(__name__)


class GroupAlarmData:
    """helper class for centrally querying the data from GroupAlarm."""

    def __init__(self, hass, api_key):
        """Initiate necessary data for the helper class."""
        self._hass = hass

        self.success = False
        self.latest_update = None

        self.data = None

        if api_key != "":
            self.api_key = api_key

    async def async_update(self):
        """Asynchronous update for all GroupAlarm entities."""
        return await self._hass.async_add_executor_job(self._update)

    def _update(self):
        """Update for all GroupAlarm entities."""
        timestamp = datetime.now()

        if not self.api_key:
            _LOGGER.exception("No update possible")
        else:
            params = {"Personal-Access-Token": self.api_key}
            try:
                response = requests.get(
                    GROUPALARM_URL, params=params, timeout=DEFAULT_TIMEOUT
                )
                self.data = response.json()
                self.success = response.status_code == 200
            except requests.exceptions.HTTPError as ex:
                _LOGGER.error("Error: %s", ex)
                self.success = False
            else:
                self.latest_update = timestamp
            _LOGGER.debug("Values updated at %s", self.latest_update)

    def get_user(self):
        """Return information about the user."""
        return {}

    def get_last_alarm_attributes(self):
        """Return aditional information of last alarm."""
        sorting_list = self.data["data"]["alarm"]["sorting"]
        if len(sorting_list) > 0:
            last_alarm_id = sorting_list[0]
            alarm = self.data["data"]["alarm"]["items"][str(last_alarm_id)]
            groups = map(self.get_group_name_by_id, alarm["group"])
            return {
                "id": alarm["id"],
                "text": alarm["text"],
                "date": datetime.fromtimestamp(alarm["date"]),
                "address": alarm["address"],
                "latitude": str(alarm["lat"]),
                "longitude": str(alarm["lng"]),
                "groups": list(groups),
                "priority": alarm["priority"],
                "closed": alarm["closed"],
                "new": alarm["new"],
                "self_addressed": alarm["ucr_self_addressed"],
            }
        else:
            return {}

    def get_last_alarm(self):
        """Return informations of last alarm."""
        sorting_list = self.data["data"]["alarm"]["sorting"]
        if len(sorting_list) > 0:
            last_alarm_id = sorting_list[0]
            alarm = self.data["data"]["alarm"]["items"][str(last_alarm_id)]
            return alarm["title"]
        else:
            return STATE_UNKNOWN

    def get_group_name_by_id(self, group_id):
        """Return the name from the given group id."""
        try:
            group = self.data["data"]["cluster"]["group"][str(group_id)]
            return group["name"]
        except KeyError:
            return None

    def set_state(self, state_id):
        """Set the state of the user to the given id."""
        payload = json.dumps({"Status": {"id": state_id}})
        headers = {"Content-Type": "application/json"}

        if not self.api_key:
            _LOGGER.exception("state can not be set. api-key is missing")
        else:
            params = {"accesskey": self.api_key}
            try:
                response = requests.post(
                    GROUPALARM_STATUS_URL,
                    params=params,
                    headers=headers,
                    timeout=DEFAULT_TIMEOUT,
                    data=payload,
                )
                if response.status_code != 200:
                    _LOGGER.error("Error while setting the state")
            except requests.exceptions.HTTPError as ex:
                _LOGGER.error("Error: %s", ex)
