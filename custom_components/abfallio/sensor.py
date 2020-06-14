"""Support for abfallio sensor devices."""
import logging
from datetime import datetime
from homeassistant.helpers.entity import Entity
from . import (
        #CONF_DATEFORMAT,
        DEFAULT_DATEFORMAT,
        DATA_ABFALL,
        DOMAIN,
        SENSOR_PREFIX
)

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the abfallio sensor platform."""
    domain='sensor'
    devices=[]
    for trash in hass.data[DATA_ABFALL].data:
        _LOGGER.debug("%s: Setup %s %s", DOMAIN, trash, domain) 
        device = AbfallSensor(SENSOR_PREFIX, hass.data[DATA_ABFALL], trash, DEFAULT_DATEFORMAT)
        devices.append(device)
    add_entities(devices)

class AbfallSensor(Entity):
    """The sensor class for abfallio sensors."""

    def __init__(self, prefix, data, sensor_type, dateformat):
        """Initialize the sensor."""
        self.data = data
        self.type = sensor_type
        self._name = prefix + "_sensor_" + self.type.lower().replace(" ","_")
        self._dateformat= str(dateformat)
        self._nextdate = None
        self._state = None
        self._unit = 'Tage bis zur Leerung'
        self._icon = 'mdi:recycle'
        self._attributes = {}
        _LOGGER.debug("Initialized sensor: %s", self._name)

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def device_state_attributes(self):
        """Return attributes for the sensor."""
        return self._attributes

    def update(self):
        """Get latest data and states from the data object."""
        _LOGGER.debug("Update sensor: %s", self._name)
        
        try:
            self._nextdate = self.data.data.get(self.type)
            if self._nextdate is not None:
                self._attributes['date'] = self._nextdate.isoformat()
                self._state = (self._nextdate.date() - datetime.now().date()).days
                if self._state == 0:
                    printtext = "heute"
                elif self._state == 1:
                    printtext = "morgen"
                else:
                    printtext = 'in {} Tagen'.format(self._state)
                #self._attributes['display_text'] = self._nextdate.strftime("{}, " + self._dateformat + " ({})").format(self._nextdate.strftime("%A"), printtext)
                self._attributes['display_text'] = self._nextdate.strftime(self._dateformat + " ({})").format(self._nextdate.strftime("%A"), printtext)

        except ValueError:
            self._state = None

