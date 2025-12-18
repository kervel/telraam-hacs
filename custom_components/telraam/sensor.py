from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities: AddEntitiesCallback):
    """Set up Telraam sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        TelraamSensor(coordinator, "car"),
        TelraamSensor(coordinator, "bike"),
        TelraamSensor(coordinator, "pedestrian"),
        TelraamSensor(coordinator, "night"),
        TelraamSensor(coordinator, "v85"),
        TelraamSensor(coordinator, "heavy"),
        MotorizedTrafficSensor(coordinator)
    ], True)

class TelraamSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, traffic_type):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._traffic_type = traffic_type
        self._attributes = {}
        self._attr_unique_id = f"{coordinator.segment_id}_{traffic_type}"  # Unique ID
        if traffic_type == 'v85':
            self._attr_name = f"85th Percentile Speed"
        elif traffic_type == 'night':
           self._attr_name = f"Night detections"
        else:
           self._attr_name = f"Telraam {traffic_type.capitalize()} Count"


    @property
    def state(self):
        svalue = self.coordinator.data.get(self._traffic_type)
        if svalue is not None:
           return float(svalue)
        return svalue

    @property
    def state_class(self):
        return "measurement"

    @property
    def device_info(self):
        """Return information about the device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.segment_id)},
            name=f"Telraam Traffic Counter ({self.coordinator.segment_id})",
            manufacturer="Telraam",
            model="API v1",
            configuration_url="https://telraam.net"
        )

    @property
    def extra_state_attributes(self):
        return self._attributes


class MotorizedTrafficSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attributes = {}
        self._attr_unique_id = f"{coordinator.segment_id}_motorized"  # Unique ID
        self._attr_name = f"Total motorized"
    @property
    def state(self):
        return float(self.coordinator.data.get("car", 0)) + float(self.coordinator.data.get("night", 0)) + float(self.coordinator.data.get("heavy", 0))

    @property
    def state_class(self):
        return "measurement"

    @property
    def device_info(self):
        """Return information about the device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.segment_id)},
            name=f"Telraam Traffic Counter ({self.coordinator.segment_id})",
            manufacturer="Telraam",
            model="API v1",
            configuration_url="https://telraam.net"
        )

    @property
    def extra_state_attributes(self):
        return self._attributes