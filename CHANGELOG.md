# Changelog

All notable changes to the Blocket (unofficial) Home Assistant integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-18

### Fixed

- **Critical bug**: Fixed 500 Internal Server Error when editing existing config entries via Options flow
  - Removed `self.config_entry` assignment in `BlocketOptionsFlow.__init__` to comply with Home Assistant's OptionsFlow pattern
  - The config_entry is now properly injected by Home Assistant instead of being manually assigned

### Added

- **Search Builder**: New guided search creation interface as alternative to pasting URLs
  - Choose between "Paste Blocket search URL" or "Build a search" when adding/editing watches
  - **Cars (Mobility)** builder:
    - Optional region selection (Stockholm, Skåne, Västra Götaland, etc. + "All Sweden")
    - Sort order selection (newest first, oldest first, price ascending/descending)
  - **Marketplace (Torget/Recommerce)** builder:
    - Category picker (Electronics, Furniture, Clothing, etc.)
    - Optional region selection
  - Builder automatically generates valid Blocket URLs using current 2026 URL schemes
  - Available in both initial setup and options/configuration flows
- Comprehensive region and category mappings for Swedish locations and product categories
- URL builder functions with proper parameter encoding

### Changed

- Config flow now uses multi-step process with input method selection
- Options flow restructured to support both URL input and search builder methods
- Updated translations (English and Swedish) for all new steps and options
- Version bumped to 0.2.0

### Tests

- Added comprehensive tests for URL builder functions
- Tests for mobility URL generation with regions and sort orders
- Tests for recommerce URL generation with categories and regions
- Validation tests ensuring builder-generated URLs are valid

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

[0.2.0]: https://github.com/Vortitron/ha-blocket/releases/tag/v0.2.0
[0.1.0]: https://github.com/Vortitron/ha-blocket/releases/tag/v0.1.0
