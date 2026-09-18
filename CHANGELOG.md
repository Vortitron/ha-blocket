# Changelog

All notable changes to the Blocket (unofficial) Home Assistant integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-18

### Added

- Initial release of unofficial Blocket integration
- Config flow for adding search URL watches
- Options flow for updating watch settings
- Polling coordinator fetching Blocket search pages
- JSON-LD parsing for listings (ItemList schema)
- Three sensor entities per watch:
  - Last listing (title + price/url attributes)
  - New listings count
  - Last poll timestamp
- `blocket_new_listing` event with stable schema
- Seed poll behaviour (no events on first poll)
- Storage of seen listing IDs
- Support for multiple watch instances
- URL validation for mobility, recommerce, and annonser paths
- English and Swedish translations
- HACS compatibility
- Polite User-Agent header
- Request timeout handling
- Proper session cleanup

### Documentation

- Comprehensive README with installation and usage
- Automation examples
- Event schema documentation
- Troubleshooting guide
- Testing guide (TESTING.md)

### Tests

- Standalone parsing tests
- Live Blocket page validation test
- URL validation tests
- Edge case handling (missing prices, etc.)

[0.1.0]: https://github.com/Vortitron/ha-blocket/releases/tag/v0.1.0
