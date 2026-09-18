"""Config flow for Blocket integration."""
import logging
import re
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
	CONF_POLL_INTERVAL,
	CONF_SEARCH_URL,
	CONF_WATCH_NAME,
	DEFAULT_POLL_INTERVAL,
	DOMAIN,
	MAX_POLL_INTERVAL,
	MIN_POLL_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


def _validate_blocket_url(url: str) -> bool:
	"""Validate that the URL is a Blocket search URL."""
	patterns = [
		r"^https?://(?:www\.)?blocket\.se/mobility/search/",
		r"^https?://(?:www\.)?blocket\.se/recommerce/forsale/search",
		r"^https?://(?:www\.)?blocket\.se/annonser/",
	]
	return any(re.match(pattern, url) for pattern in patterns)


class BlocketConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
	"""Handle a config flow for Blocket."""

	VERSION = 1

	async def async_step_user(
		self, user_input: dict[str, Any] | None = None
	) -> FlowResult:
		"""Handle the initial step."""
		errors = {}

		if user_input is not None:
			search_url = user_input[CONF_SEARCH_URL].strip()

			if not _validate_blocket_url(search_url):
				errors[CONF_SEARCH_URL] = "invalid_url"
			else:
				poll_interval = user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
				if not (MIN_POLL_INTERVAL <= poll_interval <= MAX_POLL_INTERVAL):
					errors[CONF_POLL_INTERVAL] = "invalid_interval"

			if not errors:
				watch_name = user_input.get(CONF_WATCH_NAME, "Blocket Watch")

				await self.async_set_unique_id(search_url)
				self._abort_if_unique_id_configured()

				return self.async_create_entry(
					title=watch_name,
					data={
						CONF_SEARCH_URL: search_url,
						CONF_WATCH_NAME: watch_name,
						CONF_POLL_INTERVAL: poll_interval,
					},
				)

		data_schema = vol.Schema(
			{
				vol.Required(CONF_SEARCH_URL): str,
				vol.Optional(CONF_WATCH_NAME, default="Blocket Watch"): str,
				vol.Optional(
					CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL
				): vol.All(vol.Coerce(int), vol.Range(min=MIN_POLL_INTERVAL, max=MAX_POLL_INTERVAL)),
			}
		)

		return self.async_show_form(
			step_id="user", data_schema=data_schema, errors=errors
		)

	@staticmethod
	@callback
	def async_get_options_flow(
		config_entry: config_entries.ConfigEntry,
	) -> config_entries.OptionsFlow:
		"""Get the options flow for this handler."""
		return BlocketOptionsFlow(config_entry)


class BlocketOptionsFlow(config_entries.OptionsFlow):
	"""Handle options flow for Blocket."""

	def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
		"""Initialize options flow."""
		self.config_entry = config_entry

	async def async_step_init(
		self, user_input: dict[str, Any] | None = None
	) -> FlowResult:
		"""Manage the options."""
		errors = {}

		if user_input is not None:
			search_url = user_input[CONF_SEARCH_URL].strip()

			if not _validate_blocket_url(search_url):
				errors[CONF_SEARCH_URL] = "invalid_url"
			else:
				poll_interval = user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
				if not (MIN_POLL_INTERVAL <= poll_interval <= MAX_POLL_INTERVAL):
					errors[CONF_POLL_INTERVAL] = "invalid_interval"

			if not errors:
				watch_name = user_input.get(CONF_WATCH_NAME, "Blocket Watch")

				self.hass.config_entries.async_update_entry(
					self.config_entry,
					data={
						CONF_SEARCH_URL: search_url,
						CONF_WATCH_NAME: watch_name,
						CONF_POLL_INTERVAL: poll_interval,
					},
				)

				return self.async_create_entry(title="", data={})

		current_url = self.config_entry.data.get(CONF_SEARCH_URL, "")
		current_name = self.config_entry.data.get(CONF_WATCH_NAME, "Blocket Watch")
		current_interval = self.config_entry.options.get(
			CONF_POLL_INTERVAL,
			self.config_entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
		)

		data_schema = vol.Schema(
			{
				vol.Required(CONF_SEARCH_URL, default=current_url): str,
				vol.Optional(CONF_WATCH_NAME, default=current_name): str,
				vol.Optional(CONF_POLL_INTERVAL, default=current_interval): vol.All(
					vol.Coerce(int), vol.Range(min=MIN_POLL_INTERVAL, max=MAX_POLL_INTERVAL)
				),
			}
		)

		return self.async_show_form(
			step_id="init", data_schema=data_schema, errors=errors
		)
