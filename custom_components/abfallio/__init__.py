"""The abfall.io integration."""
import logging
import requests
import csv
from datetime import datetime
from datetime import timedelta
import voluptuous as vol

from homeassistant.const import (
    CONF_URL,
    CONF_API_KEY
)
from homeassistant.helpers import discovery
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

SUPPORTED_DOMAINS = ["sensor"]
DOMAIN = 'abfallio'

CONF_ABFALLARTEN='abfallarten'
CONF_BEZIRK='bezirk'
CONF_DATEFORMAT='dateformat'
CONF_KOMMUNE='kommune'
CONF_MODBUS='modbus'
CONF_STRASSE='strasse'
CONF_ZEITRAUM='zeitraum'

DEFAULT_ABFALLARTEN=range(99)
DEFAULT_API_KEY='bd0c2d0177a0849a905cded5cb734a6f'
DEFAULT_DATEFORMAT='%d.%m.%Y'
DEFAULT_MODBUS='d6c5855a62cf32a4dadbc2831f0f295f'
DEFAULT_URL='http://api.abfall.io'
DEFAULT_ZEITRAUM='20200101-20301231'

DATA_ABFALL=DOMAIN + "_Abfall"
DATA_SENSORS=DOMAIN + "_Sensors"

SENSOR_PREFIX = 'trash'
USER_AGENT = 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'

MIN_TIME_BETWEEN_UPDATES = timedelta(days=1)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
		vol.Optional(CONF_URL, default=DEFAULT_URL): cv.url,
		vol.Optional(CONF_API_KEY, default=DEFAULT_API_KEY): cv.string,
		vol.Optional(CONF_ZEITRAUM, default=DEFAULT_ZEITRAUM): cv.string,
		vol.Optional(CONF_MODBUS, default=DEFAULT_MODBUS): cv.string,
                vol.Optional(CONF_DATEFORMAT, default=DEFAULT_DATEFORMAT): cv.string,
                #workaround - issue with syntax if DEFAULT_ABFALLARTEN defined and this validation exists
                #vol.Optional(CONF_ABFALLARTEN, default=DEFAULT_ABFALLARTEN): vol.All(cv.ensure_list, [cv.positive_int]),
                vol.Required(CONF_KOMMUNE): cv.positive_int,
		vol.Required(CONF_BEZIRK): vol.All(cv.ensure_list, [cv.positive_int]),
                vol.Required(CONF_STRASSE): vol.All(cv.ensure_list, [cv.positive_int])
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass, config):
    """Setup the abfall.io component."""
    _LOGGER.debug("Starting setup of '%s' component..", DOMAIN)
 
    #workaround - currently use all trash types 0 - 99 
    config[DOMAIN][CONF_ABFALLARTEN] = DEFAULT_ABFALLARTEN

    try:
        hass.data[DATA_ABFALL] = AbfallData(config[DOMAIN][CONF_URL],config[DOMAIN][CONF_API_KEY],
                                            config[DOMAIN][CONF_ZEITRAUM],config[DOMAIN][CONF_KOMMUNE],
                                            config[DOMAIN][CONF_BEZIRK],config[DOMAIN][CONF_STRASSE],
                                            config[DOMAIN][CONF_ABFALLARTEN],config[DOMAIN][CONF_MODBUS],
                                            config[DOMAIN][CONF_DATEFORMAT])
    except requests.exceptions.HTTPError as error:
        _LOGGER.error(error)
        return False
    hass.data[DATA_ABFALL].update()

    for domain in SUPPORTED_DOMAINS:
        _LOGGER.debug("Discover platform: %s - %s",DOMAIN, domain)
        discovery.load_platform(hass, domain, DOMAIN, {}, config)

    # Return boolean to indicate that initialization was successful.
    _LOGGER.debug("The '%s' component is ready!", DOMAIN)
    return True

class AbfallData(object):

    def __init__(self, url, key, zeitraum, kommune, bezirk, strasse, arten, modbus, dateformat):
        _LOGGER.debug("Initialize AbfallData object")
        self._url = str(url)
        self._key = str(key)
        self._zeitraum = str(zeitraum)
        self._kommune = str(kommune)
        self._bezirk = ','.join(str(x) for x in bezirk)
        self._strasse = ','.join(str(x) for x in strasse)
        self._arten = arten
        self._artenstr = ','.join(str(x) for x in arten)
        self._modbus = str(modbus)
        self._dateformat= str(dateformat)
        self.data = None
        _LOGGER.debug("Initialize complete %s", self)

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        _LOGGER.debug("Updating Abfall dates using remote API")
        try:
            headers = { "User-Agent": USER_AGENT }
            payload = {
                "f_id_kommune": self._kommune,
                "f_id_bezirk": self._bezirk,
                "f_id_strasse": self._strasse,
                "f_abfallarten": self._artenstr,
                "f_zeitraum": self._zeitraum
            }
    
            i = 0
            for trash in self._arten:
                payload['f_id_abfalltyp_' + str(i) ] = trash
                i +=1
            payload['f_abfallarten_index_max' ] = i
            #_LOGGER.debug("payload is: %s", payload)

            self._uri=self._url + "/?key=" + self._key + "&modus=" + self._modbus + "&waction=export_csv"
            #_LOGGER.debug("uri is: %s", self._uri)
            j = requests.post(self._uri, headers=headers, data=payload, timeout=10)
            #_LOGGER.debug("j is: %s", j.text)

            apiRequest = j.text.split('\n')
            #_LOGGER.debug("apiRequest is: %s", apiRequest)
            reader = csv.reader(apiRequest, delimiter=";")
            rowCounter = 0
            columns = None

            for row in reader:
                if rowCounter > 0:
                    for k in columns:
                        if (row[columns[k]] != ""):
                            trashlists[k].append(datetime.strptime(row[columns[k]], self._dateformat))
                elif rowCounter == 0:
                    columns = {k:row.index(k) for k in row}
                    trashlists = {k:[] for k in row}
                else:
                    _LOGGER.error("Invalid row counter while CSV reading: %s", rowCounter)
                    return False
                rowCounter = rowCounter + 1
            #_LOGGER.debug("columns are: %s", columns)
            #_LOGGER.debug("trashlists are: %s", trashlists) 

            nextDates = {}
            for k in columns:
                trashlists[k].sort(key=lambda date: date)
                for nextDate in trashlists[k]:
                    if nextDate > datetime.now():
                        nextDates[k] = nextDate
                        break
            _LOGGER.info("next trash dates are: %s", nextDates)
            self.data = nextDates

        except requests.exceptions.RequestException as exc:
            _LOGGER.error("Error occurred while fetching data: %r", exc)
            self.data = None
            return False

