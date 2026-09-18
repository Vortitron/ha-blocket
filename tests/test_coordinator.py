"""Tests for the Blocket coordinator."""
import pytest

from custom_components.blocket.coordinator import BlocketCoordinator


class TestBlocketCoordinator:
	"""Test BlocketCoordinator parsing logic."""

	def test_extract_listing_id_mobility(self):
		"""Test extracting listing ID from mobility URL."""
		url = "https://www.blocket.se/mobility/item/26688057"
		listing_id = BlocketCoordinator._extract_listing_id(url)
		assert listing_id == "26688057"

	def test_extract_listing_id_invalid(self):
		"""Test extracting listing ID from invalid URL."""
		url = "https://www.blocket.se/mobility/search/car"
		listing_id = BlocketCoordinator._extract_listing_id(url)
		assert listing_id is None

	def test_parse_json_ld_valid(self):
		"""Test parsing valid JSON-LD structured data."""
		html = """
		<!DOCTYPE html>
		<html>
		<head>
			<script id="seoStructuredData" type="application/ld+json">
			{
				"@context": "https://schema.org",
				"@type": "CollectionPage",
				"mainEntity": {
					"@type": "ItemList",
					"itemListElement": [
						{
							"@type": "ListItem",
							"position": 1,
							"item": {
								"@type": "Product",
								"name": "Volvo XC60",
								"brand": {"@type": "Brand", "name": "Volvo"},
								"model": "XC60",
								"offers": {
									"@type": "Offer",
									"price": "209900",
									"priceCurrency": "SEK"
								},
								"url": "https://www.blocket.se/mobility/item/26688057",
								"image": "https://images.blocketcdn.se/test.jpg"
							}
						}
					]
				}
			}
			</script>
		</head>
		</html>
		"""

		coordinator = BlocketCoordinator.__new__(BlocketCoordinator)
		listings = coordinator._parse_json_ld(html)

		assert len(listings) == 1
		assert listings[0]["listing_id"] == "26688057"
		assert listings[0]["title"] == "Volvo XC60"
		assert listings[0]["price"] == 209900
		assert listings[0]["currency"] == "SEK"
		assert listings[0]["url"] == "https://www.blocket.se/mobility/item/26688057"
		assert listings[0]["image_url"] == "https://images.blocketcdn.se/test.jpg"

	def test_parse_json_ld_no_script(self):
		"""Test parsing HTML without JSON-LD script."""
		html = "<html><body>No structured data here</body></html>"

		coordinator = BlocketCoordinator.__new__(BlocketCoordinator)
		listings = coordinator._parse_json_ld(html)

		assert listings == []

	def test_parse_json_ld_multiple_listings(self):
		"""Test parsing multiple listings."""
		html = """
		<script id="seoStructuredData" type="application/ld+json">
		{
			"@context": "https://schema.org",
			"@type": "CollectionPage",
			"mainEntity": {
				"@type": "ItemList",
				"itemListElement": [
					{
						"@type": "ListItem",
						"position": 1,
						"item": {
							"@type": "Product",
							"name": "Car 1",
							"offers": {"@type": "Offer", "price": "100000", "priceCurrency": "SEK"},
							"url": "https://www.blocket.se/mobility/item/111"
						}
					},
					{
						"@type": "ListItem",
						"position": 2,
						"item": {
							"@type": "Product",
							"name": "Car 2",
							"offers": {"@type": "Offer", "price": "200000", "priceCurrency": "SEK"},
							"url": "https://www.blocket.se/mobility/item/222"
						}
					}
				]
			}
		}
		</script>
		"""

		coordinator = BlocketCoordinator.__new__(BlocketCoordinator)
		listings = coordinator._parse_json_ld(html)

		assert len(listings) == 2
		assert listings[0]["listing_id"] == "111"
		assert listings[1]["listing_id"] == "222"
		assert listings[0]["price"] == 100000
		assert listings[1]["price"] == 200000

	def test_parse_json_ld_missing_price(self):
		"""Test parsing listing with missing price."""
		html = """
		<script id="seoStructuredData" type="application/ld+json">
		{
			"@context": "https://schema.org",
			"@type": "CollectionPage",
			"mainEntity": {
				"@type": "ItemList",
				"itemListElement": [
					{
						"@type": "ListItem",
						"position": 1,
						"item": {
							"@type": "Product",
							"name": "Free Stuff",
							"offers": {"@type": "Offer", "priceCurrency": "SEK"},
							"url": "https://www.blocket.se/mobility/item/999"
						}
					}
				]
			}
		}
		</script>
		"""

		coordinator = BlocketCoordinator.__new__(BlocketCoordinator)
		listings = coordinator._parse_json_ld(html)

		assert len(listings) == 1
		assert listings[0]["price"] is None
		assert listings[0]["currency"] == "SEK"
