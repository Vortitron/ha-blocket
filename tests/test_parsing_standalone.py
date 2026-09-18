"""Standalone tests for parsing logic (no HA dependencies)."""
import json
import re
from pathlib import Path


def extract_listing_id(url: str) -> str | None:
	"""Extract listing ID from Blocket URL."""
	match = re.search(r"/item/(\d+)", url)
	return match.group(1) if match else None


def parse_json_ld(html: str) -> list[dict]:
	"""Parse JSON-LD structured data from Blocket HTML."""
	match = re.search(
		r'<script\s+id="seoStructuredData"\s+type="application/ld\+json">(.*?)</script>',
		html,
		re.DOTALL,
	)

	if not match:
		return []

	try:
		data = json.loads(match.group(1))
	except json.JSONDecodeError:
		return []

	main_entity = data.get("mainEntity")
	if not main_entity or main_entity.get("@type") != "ItemList":
		return []

	items = main_entity.get("itemListElement", [])
	listings = []

	for item in items:
		product = item.get("item", {})
		if product.get("@type") != "Product":
			continue

		offers = product.get("offers", {})
		listing_url = product.get("url", "")
		listing_id = extract_listing_id(listing_url)

		if not listing_id:
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
				"listing_id": listing_id,
				"title": title,
				"price": price,
				"currency": offers.get("priceCurrency", "SEK"),
				"url": listing_url,
				"image_url": product.get("image"),
				"location": None,
			}
		)

	return listings


def validate_blocket_url(url: str) -> bool:
	"""Validate that the URL is a Blocket search URL."""
	patterns = [
		r"^https?://(?:www\.)?blocket\.se/mobility/search/",
		r"^https?://(?:www\.)?blocket\.se/recommerce/forsale/search",
		r"^https?://(?:www\.)?blocket\.se/annonser/",
	]
	return any(re.match(pattern, url) for pattern in patterns)


def test_extract_listing_id():
	"""Test listing ID extraction."""
	assert extract_listing_id("https://www.blocket.se/mobility/item/26688057") == "26688057"
	assert extract_listing_id("https://www.blocket.se/mobility/search/car") is None
	print("✓ Listing ID extraction tests passed")


def test_validate_url():
	"""Test URL validation."""
	assert validate_blocket_url("https://www.blocket.se/mobility/search/car?location=stockholm")
	assert validate_blocket_url("https://www.blocket.se/recommerce/forsale/search?q=laptop")
	assert validate_blocket_url("https://www.blocket.se/annonser/hela_sverige/fordon/bilar")
	assert validate_blocket_url("https://blocket.se/mobility/search/car")
	assert not validate_blocket_url("https://www.example.com/search")
	assert not validate_blocket_url("https://www.blocket.se/about")
	assert not validate_blocket_url("https://www.blocket.se/mobility/item/26688057")
	print("✓ URL validation tests passed")


def test_parse_fixture():
	"""Test parsing the fixture HTML."""
	fixture_path = Path(__file__).parent / "fixtures" / "blocket_search_sample.html"
	html = fixture_path.read_text()

	listings = parse_json_ld(html)

	assert len(listings) == 3, f"Expected 3 listings, got {len(listings)}"
	assert listings[0]["listing_id"] == "26688057"
	assert listings[0]["title"] == "Volvo XC70"
	assert listings[0]["price"] == 209900
	assert listings[0]["currency"] == "SEK"

	assert listings[1]["listing_id"] == "26688032"
	assert listings[1]["price"] == 169800

	assert listings[2]["listing_id"] == "26688004"
	assert listings[2]["price"] == 139900

	print(f"✓ Fixture parsing test passed ({len(listings)} listings)")


def test_parse_missing_data():
	"""Test parsing with missing data."""
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
						"name": "Free Item",
						"offers": {"@type": "Offer", "priceCurrency": "SEK"},
						"url": "https://www.blocket.se/mobility/item/999"
					}
				}
			]
		}
	}
	</script>
	"""

	listings = parse_json_ld(html)
	assert len(listings) == 1
	assert listings[0]["price"] is None
	assert listings[0]["currency"] == "SEK"
	print("✓ Missing data handling test passed")


if __name__ == "__main__":
	test_extract_listing_id()
	test_validate_url()
	test_parse_fixture()
	test_parse_missing_data()
	print("\n✅ All standalone tests passed!")
