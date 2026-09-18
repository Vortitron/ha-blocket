"""Tests for the Blocket config flow."""
import pytest

from custom_components.blocket.config_flow import (
	_build_mobility_url,
	_build_recommerce_url,
	_validate_blocket_url,
)


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


class TestURLBuilder:
	"""Test URL builder functions."""

	def test_build_mobility_url_all_sweden(self):
		"""Test building mobility URL for all of Sweden."""
		url = _build_mobility_url("all", "PUBLISHED_DESC")
		assert url == "https://www.blocket.se/mobility/search/car?sort=PUBLISHED_DESC"

	def test_build_mobility_url_with_region(self):
		"""Test building mobility URL with specific region."""
		url = _build_mobility_url("0.300001", "PUBLISHED_DESC")
		assert url == "https://www.blocket.se/mobility/search/car?location=0.300001&sort=PUBLISHED_DESC"

	def test_build_mobility_url_skane(self):
		"""Test building mobility URL for Skåne."""
		url = _build_mobility_url("0.300012", "PUBLISHED_DESC")
		assert url == "https://www.blocket.se/mobility/search/car?location=0.300012&sort=PUBLISHED_DESC"

	def test_build_mobility_url_price_sort(self):
		"""Test building mobility URL with price sorting."""
		url = _build_mobility_url("all", "PRICE_ASC")
		assert url == "https://www.blocket.se/mobility/search/car?sort=PRICE_ASC"

	def test_build_recommerce_url_all(self):
		"""Test building recommerce URL with no filters."""
		url = _build_recommerce_url("all", "all")
		assert url == "https://www.blocket.se/recommerce/forsale/search"

	def test_build_recommerce_url_with_category(self):
		"""Test building recommerce URL with category."""
		url = _build_recommerce_url("0.93", "all")
		assert url == "https://www.blocket.se/recommerce/forsale/search?category=0.93"

	def test_build_recommerce_url_with_region(self):
		"""Test building recommerce URL with region."""
		url = _build_recommerce_url("all", "0.300001")
		assert url == "https://www.blocket.se/recommerce/forsale/search?location=0.300001"

	def test_build_recommerce_url_category_and_region(self):
		"""Test building recommerce URL with both category and region."""
		url = _build_recommerce_url("0.93", "0.300001")
		assert url == "https://www.blocket.se/recommerce/forsale/search?category=0.93&location=0.300001"

	def test_build_recommerce_url_furniture(self):
		"""Test building recommerce URL for furniture category."""
		url = _build_recommerce_url("0.78", "all")
		assert url == "https://www.blocket.se/recommerce/forsale/search?category=0.78"

	def test_validate_builder_generated_mobility_url(self):
		"""Test that builder-generated mobility URLs are valid."""
		url = _build_mobility_url("0.300001", "PUBLISHED_DESC")
		assert _validate_blocket_url(url) is True

	def test_validate_builder_generated_recommerce_url(self):
		"""Test that builder-generated recommerce URLs are valid."""
		url = _build_recommerce_url("0.93", "0.300001")
		assert _validate_blocket_url(url) is True
