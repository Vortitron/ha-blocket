# Testing the Blocket Integration

## Quick Validation

### Standalone parsing tests (no dependencies)

```bash
python3 tests/test_parsing_standalone.py
```

Tests:
- URL validation logic
- Listing ID extraction from URLs
- JSON-LD parsing with fixtures
- Edge cases (missing price, etc.)

### Live Blocket page test (requires network + aiohttp)

```bash
pip3 install aiohttp
python3 tests/test_live_blocket.py
```

Fetches a real Blocket search page and validates:
- JSON-LD `seoStructuredData` is present
- `ItemList` structure is correct
- Listings can be parsed
- Listing IDs, titles, prices are extracted

**Note**: This test verifies the integration still works with Blocket's current page structure (as of September 2026). If Blocket changes their JSON-LD schema, this test will catch it.

## Home Assistant Integration Tests

Full integration testing requires a Home Assistant test environment. The `tests/test_*.py` files with HA imports (e.g. `test_coordinator.py`, `test_config_flow.py`) are designed for future HA test harness integration but currently require:

```bash
pip install homeassistant
pytest tests/
```

This is optional for development.

## Manual Testing in Home Assistant

1. Copy `custom_components/blocket/` to your HA `config/custom_components/` directory
2. Restart Home Assistant
3. Enable debug logging:

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.blocket: debug
```

4. Add the integration via UI:
   - Settings → Devices & Services → Add Integration → Blocket
   - Paste a Blocket search URL
   - Give it a name
   - Set poll interval (10 minutes recommended for testing)

5. Monitor logs:

```bash
tail -f home-assistant.log | grep blocket
```

6. Check entities:
   - `sensor.<watch_name>_last_listing`
   - `sensor.<watch_name>_new_listings`
   - `sensor.<watch_name>_last_poll`

7. Listen for events:

```yaml
# configuration.yaml
automation:
  - alias: "Debug Blocket events"
    trigger:
      - platform: event
        event_type: blocket_new_listing
    action:
      - service: persistent_notification.create
        data:
          title: "New Blocket Listing"
          message: >
            {{ trigger.event.data.title }} - {{ trigger.event.data.price }} {{ trigger.event.data.currency }}
            {{ trigger.event.data.url }}
```

8. Wait for the second poll (first poll seeds without events)
9. Add a test listing on Blocket (or wait for real ones)
10. Verify event fires and sensors update

## Expected Behavior

### First Poll (Seed)

```
INFO: First poll for 'Stockholm Cars': seeded with 45 listings (no events fired)
```

No `blocket_new_listing` events should fire. This prevents spam on setup.

### Subsequent Polls

If new listings appear:

```
INFO: Found 2 new listing(s) for 'Stockholm Cars'
DEBUG: Fired event blocket_new_listing: {'source': 'blocket', 'watch_id': '...', ...}
```

## Troubleshooting Tests

### Live test fails with "No seoStructuredData found"

Blocket may have changed their page structure. Check the fetched HTML and look for the JSON-LD script block. Update `coordinator.py` parsing logic if needed.

### Integration doesn't load in HA

Check logs for import errors or missing dependencies. Verify `manifest.json` requirements are installed.

### Events not firing

1. Verify first poll completed (check logs)
2. Wait for second poll
3. Check storage: `.storage/blocket.<entry_id>` should contain `seen_ids`
4. Verify listings are new (not in `seen_ids`)
5. Enable debug logging

### Listings not updating

- Check poll interval (default 10 minutes)
- Verify search URL still works in browser
- Check network connectivity from HA to blocket.se
