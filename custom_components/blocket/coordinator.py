"""Data update coordinator for Blocket."""
import asyncio
import json
import logging
import re
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
	ATTR_CURRENCY,
	ATTR_DISCOVERED_AT,
	ATTR_IMAGE_URL,
	ATTR_LISTING_ID,
	ATTR_LOCATION,
	ATTR_PRICE,
	ATTR_SOURCE,
	ATTR_TITLE,
	ATTR_URL,
	ATTR_WATCH_ID,
	ATTR_WATCH_NAME,
	CONF_POLL_INTERVAL,
	CONF_SEARCH_URL,
	CONF_WATCH_NAME,
	DOMAIN,
	EVENT_NEW_LISTING,
	REQUEST_TIMEOUT,
	USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1


class BlocketCoordinator(DataUpdateCoordinator):
	"""Coordinator to fetch Blocket listings."""

	def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
		"""Initialize coordinator."""
		self.entry = entry
		self.search_url: str = entry.data[CONF_SEARCH_URL]
		self.watch_name: str = entry.data.get(CONF_WATCH_NAME, "Blocket Watch")
		self.watch_id: str = entry.entry_id

		poll_interval = entry.options.get(
			CONF_POLL_INTERVAL, entry.data.get(CONF_POLL_INTERVAL, 10)
		)

		super().__init__(
			hass,
			_LOGGER,
			name=f"Blocket {self.watch_name}",
			update_interval=timedelta(minutes=poll_interval),
		)

		self._store = Store(
			hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}"
		)
		self._seen_ids: set[str] = set()
		self._is_first_poll = True
		self._session: aiohttp.ClientSession | None = None

	async def _async_setup(self) -> None:
		"""Load seen listing IDs from storage."""
		stored_data = await self._store.async_load()
		if stored_data and "seen_ids" in stored_data:
			self._seen_ids = set(stored_data["seen_ids"])
			_LOGGER.debug("Loaded %d seen listing IDs", len(self._seen_ids))

	async def _async_update_data(self) -> dict[str, Any]:
		"""Fetch listings from Blocket search URL."""
		if self._session is None:
			self._session = aiohttp.ClientSession()

		if not self._seen_ids:
			await self._async_setup()

		try:
			listings = await self._fetch_listings()

			new_listings = []
			for listing in listings:
				listing_id = listing[ATTR_LISTING_ID]
				if listing_id not in self._seen_ids:
					if not self._is_first_poll:
						new_listings.append(listing)
						await self._fire_event(listing)
					self._seen_ids.add(listing_id)

			if new_listings or self._is_first_poll:
				await self._store.async_save({"seen_ids": list(self._seen_ids)})

			if self._is_first_poll:
				_LOGGER.info(
					"First poll for '%s': seeded with %d listings (no events fired)",
					self.watch_name,
					len(listings),
				)
				self._is_first_poll = False
			elif new_listings:
				_LOGGER.info(
					"Found %d new listing(s) for '%s'", len(new_listings), self.watch_name
				)

			return {
				"listings": listings,
				"new_count": len(new_listings),
				"last_poll": dt_util.utcnow().isoformat(),
			}

		except Exception as err:
			raise UpdateFailed(f"Error fetching Blocket data: {err}") from err

	async def _fetch_listings(self) -> list[dict[str, Any]]:
		"""Fetch and parse listings from Blocket search page."""
		assert self._session is not None

		headers = {"User-Agent": USER_AGENT}

		try:
			async with asyncio.timeout(REQUEST_TIMEOUT):
				async with self._session.get(
					self.search_url, headers=headers
				) as response:
					response.raise_for_status()
					html = await response.text()

		except asyncio.TimeoutError as err:
			raise UpdateFailed(f"Request timeout for {self.search_url}") from err
		except aiohttp.ClientError as err:
			raise UpdateFailed(f"HTTP error: {err}") from err

		return self._parse_json_ld(html)

	def _parse_json_ld(self, html: str) -> list[dict[str, Any]]:
		"""Parse JSON-LD structured data from Blocket HTML."""
		match = re.search(
			r'<script\s+id="seoStructuredData"\s+type="application/ld\+json">(.*?)</script>',
			html,
			re.DOTALL,
		)

		if not match:
			_LOGGER.warning("No JSON-LD seoStructuredData found in page")
			return []

		try:
			data = json.loads(match.group(1))
		except json.JSONDecodeError as err:
			_LOGGER.error("Failed to parse JSON-LD: %s", err)
			return []

		main_entity = data.get("mainEntity")
		if not main_entity or main_entity.get("@type") != "ItemList":
			_LOGGER.warning("JSON-LD mainEntity is not an ItemList")
			return []

		items = main_entity.get("itemListElement", [])
		listings = []

		for item in items:
			product = item.get("item", {})
			if product.get("@type") != "Product":
				continue

			offers = product.get("offers", {})
			listing_url = product.get("url", "")

			listing_id = self._extract_listing_id(listing_url)
			if not listing_id:
				_LOGGER.debug("Could not extract listing ID from URL: %s", listing_url)
				continue

			brand = product.get("brand", {})
			brand_name = brand.get("name", "") if isinstance(brand, dict) else ""
			model = product.get("model", "")
			name = product.get("name", "")

			title = name or f"{brand_name} {model}".strip()
			if not title:
				title = product.get("description", "Unknown")

			price_str = offers.get("price")
			price = None
			if price_str:
				try:
					price = int(price_str)
				except (ValueError, TypeError):
					pass

			listings.append(
				{
					ATTR_LISTING_ID: listing_id,
					ATTR_TITLE: title,
					ATTR_PRICE: price,
					ATTR_CURRENCY: offers.get("priceCurrency", "SEK"),
					ATTR_URL: listing_url,
					ATTR_IMAGE_URL: product.get("image"),
					ATTR_LOCATION: None,
				}
			)

		_LOGGER.debug("Parsed %d listings from JSON-LD", len(listings))
		return listings

	@staticmethod
	def _extract_listing_id(url: str) -> str | None:
		"""Extract listing ID from Blocket URL."""
		match = re.search(r"/item/(\d+)", url)
		return match.group(1) if match else None

	async def _fire_event(self, listing: dict[str, Any]) -> None:
		"""Fire a Home Assistant event for a new listing."""
		event_data = {
			ATTR_SOURCE: "blocket",
			ATTR_WATCH_ID: self.watch_id,
			ATTR_WATCH_NAME: self.watch_name,
			ATTR_LISTING_ID: listing[ATTR_LISTING_ID],
			ATTR_TITLE: listing[ATTR_TITLE],
			ATTR_PRICE: listing[ATTR_PRICE],
			ATTR_CURRENCY: listing[ATTR_CURRENCY],
			ATTR_URL: listing[ATTR_URL],
			ATTR_IMAGE_URL: listing[ATTR_IMAGE_URL],
			ATTR_LOCATION: listing[ATTR_LOCATION],
			ATTR_DISCOVERED_AT: dt_util.utcnow().isoformat(),
		}

		self.hass.bus.async_fire(EVENT_NEW_LISTING, event_data)
		_LOGGER.debug("Fired event %s: %s", EVENT_NEW_LISTING, event_data)

	async def async_shutdown(self) -> None:
		"""Clean up resources."""
		if self._session:
			await self._session.close()
			self._session = None
