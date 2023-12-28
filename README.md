# Groupalarm Integration for Home Assistant
_DISCLAIMER: This project is a private open source project and doesn't have any connection with GroupAlarm or cubos Internet

This integration uses the GroupAlarm.com [REST API](https://developer.groupalarm.com/) to retrieve information and display it in Home Assitant. It is based on the [implementation for Diver24/7](https://github.com/fwmarcel/home-assistant-diver247) by fwmarcel.

## Installation

1. Add this repository to your custom repositories.
2. Install integration via HACS.
3. In the HA UI go to "Configuration" &rarr; "Integrations" click "+" and search for "GroupAlarm.com".
   _You can repeat this for as many accesskeys of different users as you like._
4. Follow the setup instructions.

## Configuration

The configuration is done via UI by inserting your accesskey in the setup dialog.

### How do you get your required access key?


### Sensor values

This integration allows you to read different values.
For example:

- state
  - id
  - timestamp
- alarm
  - id
  - text
  - date
  - address
  - lat
  - lng
  - groups
  - priority
  - closed
  - new

Some sensor sensors are disabled per default, as they contain a lot of data.

You can enable the ones you like in HA UI under "Configuration" &rarr; "Entities" &rarr; click on the filter icon on the right &rarr; Check "Show diabled entities" &rarr; Check the ones you like to enable &rarr; Click "ENABLE SELECTED" at the top &rarr; Confirm the next dialog

The sensor values will be set when the next update is scheduled by Home Assistant.
This is done every minute.

## Help and Contribution

If you find a problem, feel free to report it and I will do my best to help you.
If you have something to contribute, your help is greatly appreciated!
If you want to add a new feature, add a pull request first so we can discuss the details.