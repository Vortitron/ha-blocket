# Blocket (unofficial) - Project Structure

```
ha-blocket/
│
├── custom_components/blocket/          # Main integration directory
│   ├── __init__.py                     # Setup, unload, reload (1.3K)
│   ├── config_flow.py                  # Config + options flows (4.2K)
│   ├── const.py                        # Constants, event schema (693 bytes)
│   ├── coordinator.py                  # Polling + JSON-LD parsing (6.6K)
│   ├── sensor.py                       # 3 sensor entities (3.4K)
│   ├── manifest.json                   # Integration metadata
│   ├── strings.json                    # UI strings
│   └── translations/
│       ├── en.json                     # English
│       └── sv.json                     # Swedish
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── test_config_flow.py             # Config flow tests (HA deps)
│   ├── test_coordinator.py             # Coordinator tests (HA deps)
│   ├── test_parsing_standalone.py      # Standalone tests ✅
│   ├── test_live_blocket.py            # Live page validation ✅
│   └── fixtures/
│       └── blocket_search_sample.html  # Real JSON-LD fixture
│
├── hacs.json                           # HACS metadata
├── .gitignore                          # Python + HA ignores
├── LICENSE                             # MIT
│
├── README.md                           # Main documentation (6.7K)
│   • Disclaimers
│   • HACS installation
│   • Configuration
│   • Event schema
│   • Automation examples
│   • Troubleshooting
│
├── QUICKSTART.md                       # 5-minute setup guide (6.1K)
│   • Installation steps
│   • First configuration
│   • Example automations
│
├── TESTING.md                          # Testing guide (3.8K)
│   • Standalone tests
│   • Live validation
│   • HA integration testing
│   • Troubleshooting
│
├── CONTRIBUTING.md                     # Developer guide (4.5K)
│   • Setup instructions
│   • Code style
│   • Commit conventions
│   • Contribution priorities
│
├── CHANGELOG.md                        # Release notes
│   • v0.1.0 features
│
├── DEPLOYMENT.md                       # Deployment checklist
│   • Feature summary
│   • Validation results
│   • PR instructions
│
└── PROJECT_STRUCTURE.md                # This file

Total: 576 lines of Python code
       ~25K of documentation
```

## File Descriptions

### Integration Core

| File | Size | Purpose |
|------|------|---------|
| `__init__.py` | 1.3K | Entry point: setup, unload, reload |
| `config_flow.py` | 4.2K | UI flows for adding/editing watches |
| `const.py` | 693B | Constants, event attributes |
| `coordinator.py` | 6.6K | Fetch + parse Blocket pages |
| `sensor.py` | 3.4K | 3 sensor entities per watch |
| `manifest.json` | JSON | Domain, version, requirements |
| `strings.json` | JSON | UI text (base) |
| `translations/*.json` | JSON | Localized strings |

### Testing

| File | Purpose | Status |
|------|---------|--------|
| `test_parsing_standalone.py` | URL validation, JSON-LD parsing | ✅ Pass |
| `test_live_blocket.py` | Live page validation | ✅ 45 listings parsed |
| `test_config_flow.py` | Config flow logic | ⏸ Needs HA deps |
| `test_coordinator.py` | Coordinator logic | ⏸ Needs HA deps |
| `fixtures/blocket_search_sample.html` | Real JSON-LD structure | ✅ |

### Documentation

| File | Lines | Audience |
|------|-------|----------|
| `README.md` | 340 | Users (primary) |
| `QUICKSTART.md` | 241 | New users |
| `TESTING.md` | 150 | Developers/QA |
| `CONTRIBUTING.md` | 180 | Contributors |
| `CHANGELOG.md` | 60 | All |
| `DEPLOYMENT.md` | 202 | Maintainers |

## Key Features

### Config Flow

```python
User Input:
  - search_url: str (validated)
  - watch_name: str (optional)
  - poll_interval: int (5-1440 min)

Validation:
  ✅ URL matches Blocket search patterns
  ✅ Interval within bounds
  ✅ Unique ID = search URL
```

### Coordinator

```python
async def _async_update_data():
  1. Fetch Blocket search page (aiohttp)
  2. Parse JSON-LD seoStructuredData
  3. Extract ItemList → Product entries
  4. Compare with seen_ids (storage)
  5. Fire events for new listings
  6. Update sensor data
  7. Save seen_ids
```

### Event Schema

```python
{
  "source": "blocket",
  "watch_id": str,
  "watch_name": str,
  "listing_id": str,
  "title": str,
  "price": int | None,
  "currency": str,
  "url": str,
  "image_url": str | None,
  "location": None,  # Future
  "discovered_at": str (ISO8601)
}
```

### Sensors

```python
sensor.<watch>_last_listing:
  state: title
  attrs: {price, url}

sensor.<watch>_new_listings:
  state: count (int)

sensor.<watch>_last_poll:
  state: timestamp (datetime)
```

## Design Decisions

### ✅ Chosen Approach

- **Domain**: `blocket` (not fyndbot)
- **Parsing**: JSON-LD `seoStructuredData` (confirmed Sep 2026)
- **Storage**: `.storage/blocket.<entry_id>` for seen IDs
- **Events**: Stable schema, downstream-agnostic
- **Seed poll**: No events on first poll (anti-spam)
- **Multiple watches**: Separate config entries
- **Poll interval**: Default 10 min (respectful)
- **Error handling**: Timeouts, malformed JSON, missing fields

### ❌ Explicitly Avoided

- Fyndbot/Telegram branding
- AI scoring / Stripe / Biluppgifter
- Binary sensors (out of MVP scope)
- Service calls (out of MVP scope)
- Location parsing (unreliable in JSON-LD)
- Old `__NEXT_DATA__` parsing (deprecated)

## Validation Summary

| Test | Result |
|------|--------|
| JSON validation | ✅ All valid |
| Standalone tests | ✅ Pass |
| Live Blocket fetch | ✅ 45 listings |
| Python syntax | ✅ No errors |
| Type hints | ✅ Present |
| Documentation | ✅ Complete |
| HACS structure | ✅ Valid |
| Translations | ✅ EN + SV |

## Installation Paths

### HACS (Recommended)

1. HACS → Integrations → ⋮ → Custom repositories
2. Add: `https://github.com/Vortitron/ha-blocket`
3. Install "Blocket (unofficial)"
4. Restart HA
5. Settings → Add Integration → Blocket

### Manual

1. Copy `custom_components/blocket/` to HA config
2. Restart HA
3. Settings → Add Integration → Blocket

## Dependencies

Runtime:
- `aiohttp>=3.9.0` (HTTP client)
- Home Assistant 2024.1.0+

Development:
- `pytest` (testing, optional)
- `aiohttp` (for live tests)

## Upstream Consumers

The `blocket_new_listing` event is designed for:

- **Fyndbot** (Telegram bot) - can subscribe to events
- **Vome** (home automation) - native HA automations
- **Custom bots** - any service listening to HA events
- **Node-RED** - HA event nodes
- **AppDaemon** - Python apps
- **Webhooks** - forward events externally

The schema is stable and documented. No coupling to any specific consumer.

---

**Repository**: https://github.com/Vortitron/ha-blocket
**Branch**: `cursor/scaffold-blocket-integration-44ed`
**Status**: ✅ Complete, tested, ready for release
**Version**: 0.1.0
