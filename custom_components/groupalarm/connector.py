"""Connector Class for GroupAlarm Data."""

from datetime import datetime
import logging
import json
import requests

from homeassistant.const import STATE_UNKNOWN, STATE_OFF, STATE_ON
from .const import DEFAULT_TIMEOUT, GROUPALARM_URL

_LOGGER = logging.getLogger(__name__)


class GroupAlarmData:
    """helper class for centrally querying the data from GroupAlarm."""

    def __init__(self, hass, api_key, only_own_alarms = True):
        """Initiate necessary data for the helper class."""
        self._hass = hass

        self.success = False
        self.latest_update = None

        self.alarms = None
        self.user = None

        if api_key != "":
            self.api_key = api_key
        self.only_own_alarms = only_own_alarms != False

    async def async_update(self):
        """Asynchronous update for all GroupAlarm entities."""
        return await self._hass.async_add_executor_job(self._update)

    def _update(self):
        """Update for all GroupAlarm entities."""
        timestamp = datetime.now()

        if not self.api_key:
            _LOGGER.exception("No update possible")
        else:
            self.request_headers = {"Personal-Access-Token": self.api_key}
            try:
                if self.only_own_alarms:
                    url = GROUPALARM_URL + "/alarms/alarmed"
                else:
                    url = GROUPALARM_URL + "/alarms/user"
                _LOGGER.debug("Using alarm url: %s", url)
                alarms = requests.get(url=url, headers=self.request_headers, timeout=DEFAULT_TIMEOUT)
                _LOGGER.debug("Getting alarms returned: %s", alarms.content)
                self.alarms = alarms.json()

                user = requests.get(url=GROUPALARM_URL + "/user", headers=self.request_headers, timeout=DEFAULT_TIMEOUT)
                _LOGGER.debug("Getting user returned: %s", user.content)
                try:
                    self.user = user.json()
                except:
                    raise ValueError("Cannot parse user: %s", user.content)

                self.success = alarms.status_code == 200 and alarms.status_code == 200 
            except requests.exceptions.HTTPError as ex:
                _LOGGER.error("Error: %s", ex)
                self.success = False
            else:
                self.latest_update = timestamp
            _LOGGER.debug("Values updated at %s", self.latest_update)

    def get_user(self):
        """Return information about the user."""
        return {
            "id": self.user["id"],
            "email": self.user["email"],
            "name": self.user["name"],
            "surname": self.user["surname"],
        }

    def get_last_alarm_attributes(self):
        """Return aditional information of last alarm."""
        alarmList = self.alarms["alarms"]
        if len(alarmList) > 0:
            alarm = alarmList[0]
            try:
                feedback = self.get_user_feedback(alarm["feedback"])
                alarmed = True
            except UserNotAlarmedException:
                feedback = None
                alarmed = False
            
            return {
                "id": alarm["id"],
                "event": alarm["event"]["name"],
                "message": alarm["message"],
                "date": datetime.fromisoformat(alarm["startDate"]),
                "organization": self.get_organization_name_by_id(alarm["organizationID"]),
                "alarmed": alarmed,
                "feedback": feedback
            }
        else:
            return {}

    def get_alarm_state(self):
        """Return informations of last alarm."""
        alarmList = self.alarms["alarms"]
        if len(alarmList) > 0:
            alarm = alarmList[0]
            if (datetime.fromisoformat(alarm["startDate"]) < datetime.now().astimezone()) and (datetime.fromisoformat(alarm["endDate"]) > datetime.now().astimezone()):
                return STATE_ON
            else:
                return STATE_OFF
        else:
            return STATE_UNKNOWN

    def get_organization_name_by_id(self, organization):
        """Return the name from the given group id."""
        try:
            response = requests.get(url=GROUPALARM_URL + "/organization/" + organization, headers=self.request_headers, timeout=DEFAULT_TIMEOUT)
            _LOGGER.debug("Getting organization id %s returned: %s", organization, response.content)
            return response.json()
        except KeyError:
            return None
        
    def get_user_feedback(self, alarmFeedback):
        ownId = self.get_user()["id"]
        for feedback in alarmFeedback:
            if feedback["userID"] == ownId:
                if feedback["state"] == "WAITING":
                    return None
                else:
                    return feedback["feedback"]
        raise UserNotAlarmedException()

    def set_state(self, state_id):
        """Set the state of the user to the given id."""
        payload = json.dumps({"Status": {"id": state_id}})
        headers = {"Content-Type": "application/json"}

        if not self.api_key:
            _LOGGER.exception("state can not be set. api-key is missing")
        else:
            headers = {"Content-Type": "application/json", "accesskey": self.api_key}
            try:
                response = requests.post(
                    headers=headers,
                    timeout=DEFAULT_TIMEOUT,
                    data=payload,
                )
                if response.status_code != 200:
                    _LOGGER.error("Error while setting the state")
            except requests.exceptions.HTTPError as ex:
                _LOGGER.error("Error: %s", ex)

class UserNotAlarmedException(Exception):
    pass