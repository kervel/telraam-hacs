import aiohttp
import async_timeout
from datetime import timedelta
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

import logging


from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.util import dt as dt_util
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Telraam from a config entry."""
    session = async_get_clientsession(hass)
    coordinator = TelraamDataCoordinator(hass, session, entry.data["api_key"], entry.data["segment_id"])
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in [Platform.SENSOR]:
        await hass.config_entries.async_forward_entry_setups(entry, [platform])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, [Platform.SENSOR])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class TelraamDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Telraam data API."""

    def __init__(self, hass, session, api_key, segment_id):
        """Initialize."""
        self.api_key = api_key
        self.segment_id = segment_id
        self.session = session

        update_interval = timedelta(hours=1)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self):
        """Fetch data from API."""
        url = "https://telraam-api.net/v1/reports/traffic"
        params = {
            "level": "segments",
            "id": self.segment_id,
            "format": "per-hour",
            "time_start": (dt_util.utcnow() - timedelta(hours=2)).isoformat(),
            "time_end": dt_util.utcnow().isoformat(),
        }
        headers = {"X-Api-Key": self.api_key}

        async with self.session.post(url, headers=headers, json=params) as response:
            if response.status != 200:
                txt = await response.text()
                raise UpdateFailed(f"Error fetching data from Telraam API: {response.status} {txt}")
            data = await response.json()
            _LOGGER.debug(f"Received data from Telraam API: {data}")
            return data["report"][0] if "report" in data and data["report"] else {}
