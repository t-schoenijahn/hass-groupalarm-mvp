"""Constants for the GroupAlarm integration."""
from datetime import timedelta

DOMAIN = "groupalarm"

DEFAULT_NAME = "GroupAlarm 24/7"
DEFAULT_SHORT_NAME = "GroupAlarm"

ATTR_NAME = "state"
ATTR_LATEST_UPDATE = "latest_update_utc"
GROUPALARM_DATA = "groupalarm_data"
GROUPALARM_COORDINATOR = "groupalarm_coordinator"
GROUPALARM_NAME = "groupalarm_name"

DEFAULT_TIMEOUT = 10
GROUPALARM_URL = "https://www.groupalarm247.com/api/v2/pull/all"
GROUPALARM_STATUS_URL = "https://www.groupalarm247.com/api/v2/statusgeber/set-status"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)
