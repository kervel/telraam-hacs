import voluptuous as vol
from homeassistant import config_entries

class TelraamConfigFlow(config_entries.ConfigFlow, domain="telraam"):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Save the API key and device ID somewhere like hass.data
            return self.async_create_entry(title="Telraam", data=user_input)
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
                vol.Required("segment_id"): str,
            }),
        )
