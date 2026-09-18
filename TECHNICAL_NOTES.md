# Technical Implementation Notes

## Bug Fix: Options Flow 500 Error

### Problem Analysis

In Home Assistant, the OptionsFlow class is a special flow handler for editing existing config entries. The framework expects to inject the `config_entry` reference automatically through its internal mechanisms.

**Problematic Code (before):**
```python
class BlocketOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry  # <-- This causes the 500 error
```

When `self.config_entry = config_entry` is manually assigned in `__init__`, it interferes with Home Assistant's injection mechanism, causing the options flow to fail to load with a 500 Internal Server Error.

### Solution

**Fixed Code (after):**
```python
class BlocketOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._input_method: str | None = None
        self._marketplace_type: str | None = None
        # No self.config_entry assignment - HA injects it automatically
```

The `config_entry` is still accessible throughout the flow via `self.config_entry`, but it's now properly injected by the Home Assistant framework rather than being manually assigned.

## Feature: Search Builder

### Architecture

The search builder uses a multi-step config/options flow pattern:

```
Initial Step (user/init)
    ↓
Choose Input Method
    ├─→ Paste URL → url step → Create Entry
    └─→ Build Search → builder_type step
                          ├─→ Mobility → builder_mobility step → Create Entry
                          └─→ Recommerce → builder_recommerce step → Create Entry
```

### URL Builder Functions

Two core functions generate valid Blocket URLs:

**Mobility (Cars):**
```python
def _build_mobility_url(region: str, sort_order: str) -> str:
    base_url = "https://www.blocket.se/mobility/search/car"
    params = {}
    
    if region and region != "all":
        params["location"] = region
    
    if sort_order:
        params["sort"] = sort_order
    
    if params:
        return f"{base_url}?{urlencode(params)}"
    return base_url
```

**Recommerce (Marketplace):**
```python
def _build_recommerce_url(category: str, region: str) -> str:
    base_url = "https://www.blocket.se/recommerce/forsale/search"
    params = {}
    
    if category and category != "all":
        params["category"] = category
    
    if region and region != "all":
        params["location"] = region
    
    if params:
        return f"{base_url}?{urlencode(params)}"
    return base_url
```

### Region and Category IDs

The integration includes verified Blocket IDs for common regions and categories:

**Regions** (location parameter):
- All Sweden: `"all"` (omitted from URL)
- Stockholm: `"0.300001"`
- Skåne: `"0.300012"`
- Västra Götaland: `"0.300013"`
- (+ 18 more Swedish regions)

**Recommerce Categories** (category parameter):
- All Categories: `"all"` (omitted from URL)
- Electronics: `"0.93"`
- Furniture & Home Decor: `"0.78"`
- Clothing & Shoes: `"0.62"`
- (+ 8 more categories)

**Sort Orders** (sort parameter for Mobility):
- Newest first: `"PUBLISHED_DESC"` (default)
- Oldest first: `"PUBLISHED_ASC"`
- Lowest price first: `"PRICE_ASC"`
- Highest price first: `"PRICE_DESC"`

### State Management

The flows maintain state across steps using instance variables:

```python
class BlocketConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    def __init__(self) -> None:
        self._input_method: str | None = None      # URL or builder
        self._marketplace_type: str | None = None  # Mobility or recommerce

class BlocketOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._input_method: str | None = None
        self._marketplace_type: str | None = None
```

### Translation Structure

Each step has translations in `strings.json`, `en.json`, and `sv.json`:

```json
{
  "config": {
    "step": {
      "user": { ... },
      "url": { ... },
      "builder_type": { ... },
      "builder_mobility": { ... },
      "builder_recommerce": { ... }
    }
  },
  "options": {
    "step": {
      "init": { ... },
      "url": { ... },
      "builder_type": { ... },
      "builder_mobility": { ... },
      "builder_recommerce": { ... }
    }
  }
}
```

### Validation

All builder-generated URLs go through the same validation as manually-pasted URLs:

```python
def _validate_blocket_url(url: str) -> bool:
    patterns = [
        r"^https?://(?:www\.)?blocket\.se/mobility/search/",
        r"^https?://(?:www\.)?blocket\.se/recommerce/forsale/search",
        r"^https?://(?:www\.)?blocket\.se/annonser/",
    ]
    return any(re.match(pattern, url) for pattern in patterns)
```

This ensures consistency and prevents invalid URLs regardless of input method.

### Data Storage

The integration stores only the final URL in the config entry data:

```python
return self.async_create_entry(
    title=watch_name,
    data={
        CONF_SEARCH_URL: search_url,  # The generated or pasted URL
        CONF_WATCH_NAME: watch_name,
        CONF_POLL_INTERVAL: poll_interval,
    },
)
```

The builder parameters (region, category, sort) are not stored separately - only the final URL is persisted. This keeps the storage format identical whether the user used the builder or pasted a URL.

## Testing Strategy

### Unit Tests

The `test_config_flow.py` file includes:
1. URL validation tests (existing)
2. URL builder tests (new):
   - Mobility URL generation with various parameters
   - Recommerce URL generation with various parameters
   - Validation of generated URLs

### Standalone Test Script

`test_builders.py` provides a way to test the builder logic without a full Home Assistant environment:

```bash
$ python3 test_builders.py
Testing URL validation...
✓ URL validation tests passed

Testing mobility URL builder...
✓ Mobility URL builder tests passed

Testing recommerce URL builder...
✓ Recommerce URL builder tests passed

✅ All tests passed!
```

This is useful for quick iteration and CI/CD pipelines.

## Backwards Compatibility

The changes are fully backwards compatible:

1. **Existing Watches**: Config entries created with v0.1.0 continue to work unchanged
2. **URL Pasting**: Users can still paste URLs directly (original flow preserved)
3. **Storage Format**: No changes to how config data is stored
4. **API**: No breaking changes to the public API or event schema

The search builder is purely additive - it adds new steps and options but doesn't modify existing functionality.

## Future Enhancements

Possible future improvements:

1. **More Categories**: Add additional Blocket categories as users request them
2. **Advanced Filters**: Price ranges, condition filters, etc.
3. **URL Preview**: Show the generated URL before creating the watch
4. **URL Parsing**: Parse existing URLs back into builder parameters for editing
5. **Location Search**: Allow users to search for specific cities/municipalities

These can be added incrementally without breaking changes.
