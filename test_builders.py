#!/usr/bin/env python3
"""Standalone test for config flow URL builders."""
import re
from urllib.parse import urlencode


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


def run_tests():
	"""Run all builder tests."""
	print("Testing URL validation...")
	
	# Valid URLs
	assert _validate_blocket_url('https://www.blocket.se/mobility/search/car?location=stockholm')
	assert _validate_blocket_url('https://www.blocket.se/recommerce/forsale/search?q=laptop')
	assert _validate_blocket_url('https://www.blocket.se/annonser/hela_sverige/fordon/bilar')
	assert _validate_blocket_url('https://blocket.se/mobility/search/car')
	assert _validate_blocket_url('http://www.blocket.se/mobility/search/car')
	
	# Invalid URLs
	assert not _validate_blocket_url('https://www.example.com/search')
	assert not _validate_blocket_url('https://www.blocket.se/about')
	assert not _validate_blocket_url('https://www.blocket.se/mobility/item/26688057')
	
	print("✓ URL validation tests passed")
	
	print("\nTesting mobility URL builder...")
	
	# Test all Sweden
	url = _build_mobility_url('all', 'PUBLISHED_DESC')
	assert url == 'https://www.blocket.se/mobility/search/car?sort=PUBLISHED_DESC'
	assert _validate_blocket_url(url)
	
	# Test with region
	url = _build_mobility_url('0.300001', 'PUBLISHED_DESC')
	assert url == 'https://www.blocket.se/mobility/search/car?location=0.300001&sort=PUBLISHED_DESC'
	assert _validate_blocket_url(url)
	
	# Test Skåne
	url = _build_mobility_url('0.300012', 'PUBLISHED_DESC')
	assert url == 'https://www.blocket.se/mobility/search/car?location=0.300012&sort=PUBLISHED_DESC'
	assert _validate_blocket_url(url)
	
	# Test price sort
	url = _build_mobility_url('all', 'PRICE_ASC')
	assert url == 'https://www.blocket.se/mobility/search/car?sort=PRICE_ASC'
	assert _validate_blocket_url(url)
	
	print("✓ Mobility URL builder tests passed")
	
	print("\nTesting recommerce URL builder...")
	
	# Test all categories/regions
	url = _build_recommerce_url('all', 'all')
	assert url == 'https://www.blocket.se/recommerce/forsale/search'
	assert _validate_blocket_url(url)
	
	# Test with category
	url = _build_recommerce_url('0.93', 'all')
	assert url == 'https://www.blocket.se/recommerce/forsale/search?category=0.93'
	assert _validate_blocket_url(url)
	
	# Test with region
	url = _build_recommerce_url('all', '0.300001')
	assert url == 'https://www.blocket.se/recommerce/forsale/search?location=0.300001'
	assert _validate_blocket_url(url)
	
	# Test with both
	url = _build_recommerce_url('0.93', '0.300001')
	assert url == 'https://www.blocket.se/recommerce/forsale/search?category=0.93&location=0.300001'
	assert _validate_blocket_url(url)
	
	# Test furniture
	url = _build_recommerce_url('0.78', 'all')
	assert url == 'https://www.blocket.se/recommerce/forsale/search?category=0.78'
	assert _validate_blocket_url(url)
	
	print("✓ Recommerce URL builder tests passed")
	
	print("\n✅ All tests passed!")


if __name__ == "__main__":
	run_tests()
