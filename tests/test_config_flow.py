"""Tests for the Blocket config flow."""
from custom_components.blocket.config_flow import _validate_blocket_url


class TestConfigFlow:
	"""Test config flow validation."""

	def test_validate_mobility_url(self):
		"""Test validation of mobility search URL."""
		url = "https://www.blocket.se/mobility/search/car?location=stockholm"
		assert _validate_blocket_url(url) is True

	def test_validate_recommerce_url(self):
		"""Test validation of recommerce search URL."""
		url = "https://www.blocket.se/recommerce/forsale/search?q=laptop"
		assert _validate_blocket_url(url) is True

	def test_validate_annonser_url(self):
		"""Test validation of annonser URL."""
		url = "https://www.blocket.se/annonser/hela_sverige/fordon/bilar"
		assert _validate_blocket_url(url) is True

	def test_validate_with_www(self):
		"""Test validation with www prefix."""
		url = "https://www.blocket.se/mobility/search/car"
		assert _validate_blocket_url(url) is True

	def test_validate_without_www(self):
		"""Test validation without www prefix."""
		url = "https://blocket.se/mobility/search/car"
		assert _validate_blocket_url(url) is True

	def test_validate_http(self):
		"""Test validation with http (not https)."""
		url = "http://www.blocket.se/mobility/search/car"
		assert _validate_blocket_url(url) is True

	def test_invalid_domain(self):
		"""Test rejection of wrong domain."""
		url = "https://www.example.com/search"
		assert _validate_blocket_url(url) is False

	def test_invalid_path(self):
		"""Test rejection of non-search URL."""
		url = "https://www.blocket.se/about"
		assert _validate_blocket_url(url) is False

	def test_invalid_listing_url(self):
		"""Test rejection of individual listing URL."""
		url = "https://www.blocket.se/mobility/item/26688057"
		assert _validate_blocket_url(url) is False
