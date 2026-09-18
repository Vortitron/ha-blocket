# Blocket (unofficial) - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

**⚠️ UNOFFICIAL INTEGRATION - NOT AFFILIATED WITH BLOCKET**

This is an **unofficial**, community-built Home Assistant custom component for monitoring [Blocket.se](https://www.blocket.se) search results. It is **not** affiliated with, endorsed by, or connected to Blocket AB, Schibsted, or any official Blocket product or service.

Use at your own risk. This integration fetches publicly available listing data by polling Blocket search pages and may stop working if Blocket changes their page structure.

---

## What it does

- **Watch Blocket searches**: Add any Blocket search URL (cars, electronics, housing, etc.) as a "watch"
- **Detect new listings**: Automatically discovers new listings and fires Home Assistant events
- **Sensor entities**: Provides sensors for the latest listing, new listing count, and last poll time
- **Automation-friendly**: The `blocket_new_listing` event has a stable JSON schema for easy downstream consumption

## Installation

### Via HACS (Custom Repository)

1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click the three dots (⋮) in the top right
4. Select **Custom repositories**
5. Add repository URL: `https://github.com/Vortitron/ha-blocket`
6. Category: **Integration**
7. Click **Add**
8. Find "Blocket (unofficial)" in HACS and install it
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/blocket` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

---

## Configuration

### Add a Watch

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Blocket"
4. Paste your Blocket search URL (e.g. `https://www.blocket.se/mobility/search/car?location=stockholm`)
5. Give it a friendly name (e.g. "Stockholm Cars")
6. Set poll interval in minutes (default: 10, min: 5, max: 1440)

**Supported URL formats:**

- Mobility: `https://www.blocket.se/mobility/search/car?...`
- Recommerce: `https://www.blocket.se/recommerce/forsale/search?...`
- Legacy annonser: `https://www.blocket.se/annonser/...`

### Multiple Watches

You can add multiple watches (e.g. one for cars in Stockholm, another for electronics in Gothenburg). Each watch is a separate config entry with its own sensors and events.

### Options

After adding a watch, click **Configure** on the integration to update:

- Search URL
- Watch name
- Poll interval

---

## Entities

Each watch creates three sensor entities:

| Entity | Description | Example |
|--------|-------------|---------|
| `sensor.<watch_name>_last_listing` | Title of the most recent listing | "Volvo XC60" |
| `sensor.<watch_name>_new_listings` | Count of new listings found in last poll | `2` |
| `sensor.<watch_name>_last_poll` | Timestamp of last successful poll | `2026-09-18T13:45:00Z` |

The `last_listing` sensor includes attributes:

- `price`: Listing price (integer, SEK)
- `url`: Direct link to listing

---

## Events

When a **new** listing is discovered (after the initial seed poll), the integration fires a `blocket_new_listing` event on the Home Assistant event bus.

### Event Schema

```json
{
  "source": "blocket",
  "watch_id": "<config_entry_id>",
  "watch_name": "Stockholm Cars",
  "listing_id": "26688057",
  "title": "Volvo XC70",
  "price": 209900,
  "currency": "SEK",
  "url": "https://www.blocket.se/mobility/item/26688057",
  "image_url": "https://images.blocketcdn.se/...",
  "location": null,
  "discovered_at": "2026-09-18T13:45:23.123456+00:00"
}
```

**Note**: The first poll after adding a watch **does not fire events** (seeding behavior to avoid spam). Only listings discovered on subsequent polls trigger events.

---

## Automation Examples

### Send Telegram notification on new listing

```yaml
automation:
  - alias: "Notify on new Blocket listing"
    trigger:
      - platform: event
        event_type: blocket_new_listing
    action:
      - service: notify.telegram
        data:
          title: "New Blocket: {{ trigger.event.data.title }}"
          message: >
            {{ trigger.event.data.price }} {{ trigger.event.data.currency }}
            {{ trigger.event.data.url }}
```

### Filter by price

```yaml
automation:
  - alias: "Cheap car alert"
    trigger:
      - platform: event
        event_type: blocket_new_listing
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.price < 150000 }}"
    action:
      - service: notify.mobile_app
        data:
          message: "Cheap car: {{ trigger.event.data.title }} - {{ trigger.event.data.price }} SEK"
```

### Multiple watches, different actions

```yaml
automation:
  - alias: "Stockholm car alert"
    trigger:
      - platform: event
        event_type: blocket_new_listing
        event_data:
          watch_name: "Stockholm Cars"
    action:
      - service: notify.telegram
        data:
          message: "New car in Stockholm!"

  - alias: "Electronics alert"
    trigger:
      - platform: event
        event_type: blocket_new_listing
        event_data:
          watch_name: "Electronics"
    action:
      - service: notify.discord
        data:
          message: "New gadget!"
```

---

## Downstream Integration Examples

The stable `blocket_new_listing` event schema is designed for easy consumption by:

- **Telegram bots** (e.g. Fyndbot)
- **Discord/Slack webhooks**
- **Node-RED flows**
- **Custom scripts / AppDaemon**
- **Vome automations**

The integration is deliberately **not** branded or coupled to any specific downstream consumer. It provides the event; you wire it up however you like.

---

## Troubleshooting

### No events firing

- Check that listings are being found: look at `sensor.<watch>_last_listing`
- Remember: the **first poll after setup** does not fire events (seeding)
- Check Home Assistant logs for errors: `tail -f home-assistant.log | grep blocket`

### Invalid URL error

Make sure you're using a current Blocket search URL format. As of September 2026:

- ✅ `https://www.blocket.se/mobility/search/car?location=...`
- ✅ `https://www.blocket.se/annonser/hela_sverige/fordon/bilar`
- ❌ Old redirected URLs may not work

### Listings not updating

- Verify poll interval: default is 10 minutes
- Check network: can Home Assistant reach `blocket.se`?
- Enable debug logging:

```yaml
logger:
  default: info
  logs:
    custom_components.blocket: debug
```

### Integration stopped working after Blocket site update

Blocket may change their page structure. If the JSON-LD `seoStructuredData` format changes, this integration may break. Open an issue on GitHub with example URLs.

---

## Development / Contributing

PRs welcome! This is a community project.

### Running tests (TODO)

```bash
pytest tests/
```

### Local testing

1. Copy to `config/custom_components/blocket/`
2. Restart HA with debug logging enabled
3. Add a watch via UI
4. Monitor logs: `tail -f home-assistant.log | grep blocket`

---

## Disclaimers

1. **Unofficial**: This integration is not affiliated with Blocket AB, Schibsted Media Group, or any official Blocket product.
2. **No warranty**: Use at your own risk. The integration may break if Blocket changes their website.
3. **Rate limiting**: Be respectful. Default poll interval is 10 minutes; do not set it below 5 minutes.
4. **Terms of Service**: Ensure your use complies with Blocket's ToS. This integration performs the same HTTP requests a browser would.
5. **Privacy**: No data is sent anywhere except to Blocket.se to fetch search results. All processing happens locally in your Home Assistant instance.

---

## License

MIT License - see [LICENSE](LICENSE)

---

## Acknowledgments

- Inspired by various HACS integrations and the Home Assistant community
- Not affiliated with [Fyndbot](https://github.com/Vortitron/fyndbot) (a separate Telegram bot project that may consume these events)
- Thanks to Blocket for providing structured data in their search pages

---

**Questions or issues?** Open an issue on [GitHub](https://github.com/Vortitron/ha-blocket/issues).

**Want to integrate this with your own bot/automation?** The `blocket_new_listing` event schema is stable and documented above. Build whatever you want on top of it!
