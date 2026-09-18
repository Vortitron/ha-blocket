# Pull Request: Fix Options Flow 500 Error and Add Search Builder Feature

## Branch
`cursor/fix-options-flow-and-search-builder-a659`

**GitHub PR URL (to create):**
https://github.com/Vortitron/ha-blocket/pull/new/cursor/fix-options-flow-and-search-builder-a659

---

## Overview

This PR fixes a critical bug and adds a requested feature to the Blocket (unofficial) Home Assistant integration.

## Bug Fix (Priority)

**Issue**: Editing an existing config entry via Settings → Devices & Services → Blocket (unofficial) → Configure would fail with:
```
Config flow could not be loaded: 500 Internal Server Error
Server got itself in trouble
```

**Root Cause**: The `BlocketOptionsFlow.__init__` was manually assigning `self.config_entry = config_entry`, which conflicts with Home Assistant's OptionsFlow pattern. In recent HA versions, the framework injects `config_entry` automatically, and manual assignment causes the options flow to fail to load.

**Fix**: Removed the `self.config_entry = config_entry` assignment from `BlocketOptionsFlow.__init__`. The `config_entry` is now properly accessed via `self.config_entry` after HA's automatic injection.

## New Feature: Search Builder

Added a guided search builder as an alternative to pasting raw Blocket URLs, making it easier for users to create and edit watches.

### User Flow

When adding or editing a watch, users now choose between:
- **Paste Blocket search URL** (existing behaviour)
- **Build a search** (new guided flow)

### Builder Options

#### Cars (Mobility)
- **Region**: All Sweden, Stockholm, Skåne, Västra Götaland, Uppsala, etc. (21 regions)
- **Sort Order**: Newest first (default), oldest first, lowest price first, highest price first
- **Watch Name**: Custom name for the watch
- **Poll Interval**: Minutes between polls (5-1440)

#### Marketplace (Torget/Recommerce)
- **Category**: All categories, Electronics, Furniture, Clothing, Hobby, Home & Garden, etc. (11 categories)
- **Region**: Same as above
- **Watch Name**: Custom name
- **Poll Interval**: Minutes between polls

The builder automatically generates valid Blocket URLs using the current 2026 URL schemes:
- Mobility: `https://www.blocket.se/mobility/search/car?location=...&sort=...`
- Recommerce: `https://www.blocket.se/recommerce/forsale/search?category=...&location=...`

## Changes Made

### Core Changes
- `config_flow.py`: 
  - Removed problematic `self.config_entry` assignment in `BlocketOptionsFlow.__init__`
  - Restructured config flow to use multi-step process with input method selection
  - Added URL builder functions (`_build_mobility_url`, `_build_recommerce_url`)
  - Implemented builder steps for both initial setup and options flows
- `const.py`: Added constants for regions, categories, sort orders, marketplace types

### Translations
- Updated `strings.json`, `en.json`, `sv.json` with new step descriptions and field labels
- All new UI text available in both English and Swedish

### Testing
- Added comprehensive tests for URL builder functions
- Tests verify URLs are properly constructed and valid
- Standalone test script for verification without full HA environment

### Documentation
- Updated `CHANGELOG.md` with detailed v0.2.0 release notes
- Version bumped to 0.2.0 in `manifest.json`
- Updated `USER_AGENT` to reflect new version

## Testing Notes

### Options Flow Fix Testing
1. Install the integration and add a watch
2. Go to Settings → Devices & Services → Blocket (unofficial)
3. Click **Configure** on an existing watch
4. ✅ Options flow should load without 500 error
5. Update settings and save
6. ✅ Settings should update and reload work correctly

### Search Builder Testing

**Mobility Builder:**
1. Add new integration
2. Choose "Build a search"
3. Select "Cars (Mobility)"
4. Choose region (e.g., Stockholm) and sort order
5. ✅ Watch should be created with valid mobility URL
6. ✅ Watch should start polling and detecting cars

**Recommerce Builder:**
1. Add new integration
2. Choose "Build a search"
3. Select "Marketplace (Torget/Recommerce)"
4. Choose category (e.g., Electronics) and region
5. ✅ Watch should be created with valid recommerce URL
6. ✅ Watch should start polling and detecting listings

**Options Builder:**
1. Configure an existing watch
2. Choose "Build a search" instead of URL
3. ✅ Should be able to switch from URL to builder
4. Build a new search
5. ✅ Watch should update with new URL

### Unit Tests
Run the standalone test script:
```bash
python3 test_builders.py
```
✅ All URL validation and builder tests pass

## Backwards Compatibility

- ✅ Existing watches continue to work (URL validation unchanged)
- ✅ Users can still paste URLs directly (original flow preserved)
- ✅ No breaking changes to stored config data
- ✅ Search builder is purely additive

## Known Limitations

- Builder includes a curated set of regions and categories (verified common ones)
- Advanced users can still paste custom URLs for edge cases
- Category/region IDs are based on current Blocket URL patterns (Sept 2026)

## Checklist

- [x] Bug fix: Options flow no longer causes 500 error
- [x] Feature: Search builder implemented for add and edit flows
- [x] Tests updated and passing
- [x] Translations updated (English and Swedish)
- [x] Version bumped to 0.2.0
- [x] CHANGELOG.md updated
- [x] Backwards compatible
- [x] Branding kept as "Blocket (unofficial)"

## Files Changed

- `custom_components/blocket/config_flow.py` - Core fixes and builder implementation
- `custom_components/blocket/const.py` - Added region/category/sort constants
- `custom_components/blocket/manifest.json` - Version bump to 0.2.0
- `custom_components/blocket/strings.json` - UI translations
- `custom_components/blocket/translations/en.json` - English translations
- `custom_components/blocket/translations/sv.json` - Swedish translations
- `tests/test_config_flow.py` - Updated tests for builder functions
- `test_builders.py` - New standalone test script
- `CHANGELOG.md` - v0.2.0 release notes

## To Create the PR

Visit: https://github.com/Vortitron/ha-blocket/pull/new/cursor/fix-options-flow-and-search-builder-a659

Use the PR title and body from this document.
