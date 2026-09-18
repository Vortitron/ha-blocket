"""Config flow for Blocket integration."""
import logging
import re
from typing import Any
from urllib.parse import urlencode

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
	CONF_CATEGORY,
	CONF_INPUT_METHOD,
	CONF_MARKETPLACE_TYPE,
	CONF_POLL_INTERVAL,
	CONF_REGION,
	CONF_SEARCH_URL,
	CONF_SORT_ORDER,
	CONF_WATCH_NAME,
	DEFAULT_POLL_INTERVAL,
	DOMAIN,
	INPUT_METHOD_BUILDER,
	INPUT_METHOD_URL,
	MARKETPLACE_MOBILITY,
	MARKETPLACE_RECOMMERCE,
	MAX_POLL_INTERVAL,
	MIN_POLL_INTERVAL,
	RECOMMERCE_CATEGORIES,
	REGIONS,
	SORT_ORDERS,
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


def _build_mobility_url(region: str, sort_order: str) -> str:
	"""Build a Blocket mobility (cars) search URL."""
	base_url = "https://www.blocket.se/mobility/search/car"
	params = {}
	
	if region and region != "all":
		params["location"] = region
	
	if sort_order:
		params["sort"] = sort_order
	
	if params:
		return f"{base_url}?{urlencode(params)}"
	return base_url


def _build_recommerce_url(category: str, region: str) -> str:
	"""Build a Blocket recommerce search URL."""
	base_url = "https://www.blocket.se/recommerce/forsale/search"
	params = {}
	
	if category and category != "all":
		params["category"] = category
	
	if region and region != "all":
		params["location"] = region
	
	if params:
		return f"{base_url}?{urlencode(params)}"
	return base_url


class BlocketConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
	"""Handle a config flow for Blocket."""

	VERSION = 1

	def __init__(self) -> None:
		"""Initialize the config flow."""
		self._input_method: str | None = None
		self._marketplace_type: str | None = None

	async def async_step_user(
		self, user_input: dict[str, Any] | None = None
	) -> FlowResult:
		"""Handle the initial step - choose input method."""
		if user_input is not None:
			self._input_method = user_input[CONF_INPUT_METHOD]
			
			if self._input_method == INPUT_METHOD_URL:
				return await self.async_step_url()
			else:
				return await self.async_step_builder_type()
		
		data_schema = vol.Schema(
			{
				vol.Required(CONF_INPUT_METHOD, default=INPUT_METHOD_URL): vol.In(
					{
						INPUT_METHOD_URL: "Paste Blocket search URL",
						INPUT_METHOD_BUILDER: "Build a search",
					}
				),
			}
		)
		
		return self.async_show_form(
			step_id="user", data_schema=data_schema
		)

	async def async_step_url(
		self, user_input: dict[str, Any] | None = None
	) -> FlowResult:
		"""Handle URL input."""
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
			step_id="url", data_schema=data_schema, errors=errors
		)

	async def async_step_builder_type(
		self, user_input: dict[str, Any] | None = None
	) -> FlowResult:
		"""Handle marketplace type selection for builder."""
		if user_input is not None:
			self._marketplace_type = user_input[CONF_MARKETPLACE_TYPE]
			
			if self._marketplace_type == MARKETPLACE_MOBILITY:
				return await self.async_step_builder_mobility()
			else:
				return await self.async_step_builder_recommerce()
		
		data_schema = vol.Schema(
			{
				vol.Required(CONF_MARKETPLACE_TYPE): vol.In(
					{
						MARKETPLACE_MOBILITY: "Cars (Mobility)",
						MARKETPLACE_RECOMMERCE: "Marketplace (Torget/Recommerce)",
					}
				),
			}
		)
		
		return self.async_show_form(
			step_id="builder_type", data_schema=data_schema
		)

	async def async_step_builder_mobility(
		self, user_input: dict[str, Any] | None = None
	) -> FlowResult:
		"""Handle mobility search builder."""
		errors = {}

		if user_input is not None:
			region = user_input.get(CONF_REGION, "all")
			sort_order = user_input.get(CONF_SORT_ORDER, "PUBLISHED_DESC")
			watch_name = user_input.get(CONF_WATCH_NAME, "Blocket Cars")
			poll_interval = user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

			if not (MIN_POLL_INTERVAL <= poll_interval <= MAX_POLL_INTERVAL):
				errors[CONF_POLL_INTERVAL] = "invalid_interval"

			if not errors:
				search_url = _build_mobility_url(region, sort_order)

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
				vol.Optional(CONF_REGION, default="all"): vol.In(REGIONS),
				vol.Optional(CONF_SORT_ORDER, default="PUBLISHED_DESC"): vol.In(SORT_ORDERS),
				vol.Optional(CONF_WATCH_NAME, default="Blocket Cars"): str,
				vol.Optional(
					CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL
				): vol.All(vol.Coerce(int), vol.Range(min=MIN_POLL_INTERVAL, max=MAX_POLL_INTERVAL)),
			}
		)

		return self.async_show_form(
			step_id="builder_mobility", data_schema=data_schema, errors=errors
		)

	async def async_step_builder_recommerce(
		self, user_input: dict[str, Any] | None = None
	) -> FlowResult:
		"""Handle recommerce search builder."""
		errors = {}

		if user_input is not None:
			category = user_input.get(CONF_CATEGORY, "all")
			region = user_input.get(CONF_REGION, "all")
			watch_name = user_input.get(CONF_WATCH_NAME, "Blocket Marketplace")
			poll_interval = user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

			if not (MIN_POLL_INTERVAL <= poll_interval <= MAX_POLL_INTERVAL):
				errors[CONF_POLL_INTERVAL] = "invalid_interval"

			if not errors:
				search_url = _build_recommerce_url(category, region)

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
				vol.Optional(CONF_CATEGORY, default="all"): vol.In(RECOMMERCE_CATEGORIES),
				vol.Optional(CONF_REGION, default="all"): vol.In(REGIONS),
				vol.Optional(CONF_WATCH_NAME, default="Blocket Marketplace"): str,
				vol.Optional(
					CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL
				): vol.All(vol.Coerce(int), vol.Range(min=MIN_POLL_INTERVAL, max=MAX_POLL_INTERVAL)),
			}
		)

		return self.async_show_form(
			step_id="builder_recommerce", data_schema=data_schema, errors=errors
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
		self._input_method: str | None = None
		self._marketplace_type: str | None = None

	async def async_step_init(
		self, user_input: dict[str, Any] | None = None
	) -> FlowResult:
		"""Handle the initial options step - choose input method."""
		if user_input is not None:
			self._input_method = user_input[CONF_INPUT_METHOD]
			
			if self._input_method == INPUT_METHOD_URL:
				return await self.async_step_url()
			else:
				return await self.async_step_builder_type()
		
		data_schema = vol.Schema(
			{
				vol.Required(CONF_INPUT_METHOD, default=INPUT_METHOD_URL): vol.In(
					{
						INPUT_METHOD_URL: "Paste Blocket search URL",
						INPUT_METHOD_BUILDER: "Build a search",
					}
				),
			}
		)
		
		return self.async_show_form(
			step_id="init", data_schema=data_schema
		)

	async def async_step_url(
		self, user_input: dict[str, Any] | None = None
	) -> FlowResult:
		"""Handle URL input in options."""
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
			step_id="url", data_schema=data_schema, errors=errors
		)

	async def async_step_builder_type(
		self, user_input: dict[str, Any] | None = None
	) -> FlowResult:
		"""Handle marketplace type selection for builder in options."""
		if user_input is not None:
			self._marketplace_type = user_input[CONF_MARKETPLACE_TYPE]
			
			if self._marketplace_type == MARKETPLACE_MOBILITY:
				return await self.async_step_builder_mobility()
			else:
				return await self.async_step_builder_recommerce()
		
		data_schema = vol.Schema(
			{
				vol.Required(CONF_MARKETPLACE_TYPE): vol.In(
					{
						MARKETPLACE_MOBILITY: "Cars (Mobility)",
						MARKETPLACE_RECOMMERCE: "Marketplace (Torget/Recommerce)",
					}
				),
			}
		)
		
		return self.async_show_form(
			step_id="builder_type", data_schema=data_schema
		)

	async def async_step_builder_mobility(
		self, user_input: dict[str, Any] | None = None
	) -> FlowResult:
		"""Handle mobility search builder in options."""
		errors = {}

		if user_input is not None:
			region = user_input.get(CONF_REGION, "all")
			sort_order = user_input.get(CONF_SORT_ORDER, "PUBLISHED_DESC")
			watch_name = user_input.get(CONF_WATCH_NAME, "Blocket Cars")
			poll_interval = user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

			if not (MIN_POLL_INTERVAL <= poll_interval <= MAX_POLL_INTERVAL):
				errors[CONF_POLL_INTERVAL] = "invalid_interval"

			if not errors:
				search_url = _build_mobility_url(region, sort_order)

				self.hass.config_entries.async_update_entry(
					self.config_entry,
					data={
						CONF_SEARCH_URL: search_url,
						CONF_WATCH_NAME: watch_name,
						CONF_POLL_INTERVAL: poll_interval,
					},
				)

				return self.async_create_entry(title="", data={})

		current_name = self.config_entry.data.get(CONF_WATCH_NAME, "Blocket Cars")
		current_interval = self.config_entry.options.get(
			CONF_POLL_INTERVAL,
			self.config_entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
		)

		data_schema = vol.Schema(
			{
				vol.Optional(CONF_REGION, default="all"): vol.In(REGIONS),
				vol.Optional(CONF_SORT_ORDER, default="PUBLISHED_DESC"): vol.In(SORT_ORDERS),
				vol.Optional(CONF_WATCH_NAME, default=current_name): str,
				vol.Optional(CONF_POLL_INTERVAL, default=current_interval): vol.All(
					vol.Coerce(int), vol.Range(min=MIN_POLL_INTERVAL, max=MAX_POLL_INTERVAL)
				),
			}
		)

		return self.async_show_form(
			step_id="builder_mobility", data_schema=data_schema, errors=errors
		)

	async def async_step_builder_recommerce(
		self, user_input: dict[str, Any] | None = None
	) -> FlowResult:
		"""Handle recommerce search builder in options."""
		errors = {}

		if user_input is not None:
			category = user_input.get(CONF_CATEGORY, "all")
			region = user_input.get(CONF_REGION, "all")
			watch_name = user_input.get(CONF_WATCH_NAME, "Blocket Marketplace")
			poll_interval = user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

			if not (MIN_POLL_INTERVAL <= poll_interval <= MAX_POLL_INTERVAL):
				errors[CONF_POLL_INTERVAL] = "invalid_interval"

			if not errors:
				search_url = _build_recommerce_url(category, region)

				self.hass.config_entries.async_update_entry(
					self.config_entry,
					data={
						CONF_SEARCH_URL: search_url,
						CONF_WATCH_NAME: watch_name,
						CONF_POLL_INTERVAL: poll_interval,
					},
				)

				return self.async_create_entry(title="", data={})

		current_name = self.config_entry.data.get(CONF_WATCH_NAME, "Blocket Marketplace")
		current_interval = self.config_entry.options.get(
			CONF_POLL_INTERVAL,
			self.config_entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
		)

		data_schema = vol.Schema(
			{
				vol.Optional(CONF_CATEGORY, default="all"): vol.In(RECOMMERCE_CATEGORIES),
				vol.Optional(CONF_REGION, default="all"): vol.In(REGIONS),
				vol.Optional(CONF_WATCH_NAME, default=current_name): str,
				vol.Optional(CONF_POLL_INTERVAL, default=current_interval): vol.All(
					vol.Coerce(int), vol.Range(min=MIN_POLL_INTERVAL, max=MAX_POLL_INTERVAL)
				),
			}
		)

		return self.async_show_form(
			step_id="builder_recommerce", data_schema=data_schema, errors=errors
		)
