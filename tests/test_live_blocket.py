"""Test parsing against a live Blocket page (network required)."""
import asyncio
import json
import re
import sys

import aiohttp


async def fetch_and_parse(url: str) -> None:
	"""Fetch a live Blocket page and test parsing."""
	headers = {
		"User-Agent": "HomeAssistant-Blocket-unofficial/0.1.0 (https://github.com/Vortitron/ha-blocket)"
	}

	print(f"Fetching: {url}")

	async with aiohttp.ClientSession() as session:
		async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
			response.raise_for_status()
			html = await response.text()

	print(f"✓ Fetched {len(html)} bytes")

	match = re.search(
		r'<script\s+id="seoStructuredData"\s+type="application/ld\+json">(.*?)</script>',
		html,
		re.DOTALL,
	)

	if not match:
		print("✗ No seoStructuredData JSON-LD found in page")
		sys.exit(1)

	print("✓ Found seoStructuredData JSON-LD block")

	try:
		data = json.loads(match.group(1))
	except json.JSONDecodeError as err:
		print(f"✗ Failed to parse JSON-LD: {err}")
		sys.exit(1)

	print("✓ Parsed JSON-LD successfully")

	main_entity = data.get("mainEntity")
	if not main_entity or main_entity.get("@type") != "ItemList":
		print("✗ mainEntity is not an ItemList")
		sys.exit(1)

	print("✓ mainEntity is ItemList")

	items = main_entity.get("itemListElement", [])
	print(f"✓ Found {len(items)} itemListElement entries")

	if not items:
		print("⚠ No listings found (empty search?)")
		return

	listing_count = 0
	for item in items:
		product = item.get("item", {})
		if product.get("@type") != "Product":
			continue

		listing_count += 1
		listing_url = product.get("url", "")
		match = re.search(r"/item/(\d+)", listing_url)
		listing_id = match.group(1) if match else None

		if not listing_id:
			print(f"⚠ Could not extract listing ID from: {listing_url}")
			continue

		offers = product.get("offers", {})
		price = offers.get("price")
		currency = offers.get("priceCurrency", "SEK")
		name = product.get("name", "")

		print(f"  - [{listing_id}] {name} - {price} {currency}")

	print(f"\n✅ Successfully parsed {listing_count} listings from live page")


if __name__ == "__main__":
	test_urls = [
		"https://www.blocket.se/mobility/search/car",
	]

	for test_url in test_urls:
		try:
			asyncio.run(fetch_and_parse(test_url))
		except Exception as err:
			print(f"✗ Error: {err}")
			sys.exit(1)
