"""Sensor platform for Blocket integration."""
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_PRICE, ATTR_TITLE, ATTR_URL, DOMAIN
from .coordinator import BlocketCoordinator


async def async_setup_entry(
	hass: HomeAssistant,
	entry: ConfigEntry,
	async_add_entities: AddEntitiesCallback,
) -> None:
	"""Set up Blocket sensors from a config entry."""
	coordinator: BlocketCoordinator = hass.data[DOMAIN][entry.entry_id]

	async_add_entities(
		[
			BlocketLastListingSensor(coordinator),
			BlocketNewCountSensor(coordinator),
			BlocketLastPollSensor(coordinator),
		]
	)


class BlocketSensorBase(CoordinatorEntity, SensorEntity):
	"""Base class for Blocket sensors."""

	def __init__(self, coordinator: BlocketCoordinator, sensor_type: str) -> None:
		"""Initialize sensor."""
		super().__init__(coordinator)
		self._attr_has_entity_name = True
		self._attr_unique_id = f"{coordinator.entry.entry_id}_{sensor_type}"
		self._attr_device_info = {
			"identifiers": {(DOMAIN, coordinator.entry.entry_id)},
			"name": coordinator.watch_name,
			"manufacturer": "Blocket (unofficial)",
			"model": "Search Watch",
		}


class BlocketLastListingSensor(BlocketSensorBase):
	"""Sensor for the most recent listing."""

	def __init__(self, coordinator: BlocketCoordinator) -> None:
		"""Initialize last listing sensor."""
		super().__init__(coordinator, "last_listing")
		self._attr_name = "Last Listing"
		self._attr_icon = "mdi:tag"

	@property
	def native_value(self) -> str | None:
		"""Return the title of the most recent listing."""
		listings = self.coordinator.data.get("listings", [])
		if not listings:
			return None

		return listings[0].get(ATTR_TITLE)

	@property
	def extra_state_attributes(self) -> dict[str, Any] | None:
		"""Return additional attributes."""
		listings = self.coordinator.data.get("listings", [])
		if not listings:
			return None

		latest = listings[0]
		return {
			"price": latest.get(ATTR_PRICE),
			"url": latest.get(ATTR_URL),
		}


class BlocketNewCountSensor(BlocketSensorBase):
	"""Sensor for count of new listings in last poll."""

	def __init__(self, coordinator: BlocketCoordinator) -> None:
		"""Initialize new count sensor."""
		super().__init__(coordinator, "new_count")
		self._attr_name = "New Listings"
		self._attr_icon = "mdi:counter"
		self._attr_native_unit_of_measurement = "listings"

	@property
	def native_value(self) -> int:
		"""Return the count of new listings."""
		return self.coordinator.data.get("new_count", 0)


class BlocketLastPollSensor(BlocketSensorBase):
	"""Sensor for last successful poll timestamp."""

	def __init__(self, coordinator: BlocketCoordinator) -> None:
		"""Initialize last poll sensor."""
		super().__init__(coordinator, "last_poll")
		self._attr_name = "Last Poll"
		self._attr_icon = "mdi:clock-outline"
		self._attr_device_class = "timestamp"

	@property
	def native_value(self) -> datetime | None:
		"""Return the last poll timestamp."""
		last_poll_str = self.coordinator.data.get("last_poll")
		if not last_poll_str:
			return None

		return datetime.fromisoformat(last_poll_str)
