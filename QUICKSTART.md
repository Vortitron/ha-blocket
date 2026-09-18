# Quick Start Guide

Get the Blocket (unofficial) integration running in 5 minutes.

## Prerequisites

- Home Assistant 2024.1.0 or later
- HACS installed

## Installation

### Option 1: HACS Custom Repository (Recommended)

1. Open HACS in Home Assistant
2. Click **Integrations**
3. Click the three dots (⋮) in the top right
4. Select **Custom repositories**
5. Add:
   - **Repository**: `https://github.com/Vortitron/ha-blocket`
   - **Category**: Integration
6. Click **Add**
7. Find "Blocket (unofficial)" in HACS
8. Click **Download**
9. Restart Home Assistant

### Option 2: Manual

1. Download this repository
2. Copy `custom_components/blocket/` to your HA `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

### Step 1: Find Your Blocket Search URL

1. Go to [Blocket.se](https://www.blocket.se)
2. Search for what you want (e.g. cars in Stockholm, electronics, apartments)
3. Apply filters, location, price range, etc.
4. Copy the URL from your browser

**Example URLs:**

```
https://www.blocket.se/mobility/search/car?location=stockholm&price_from=100000&price_to=200000
https://www.blocket.se/annonser/hela_sverige/elektronik/datorer_tillbehor
https://www.blocket.se/recommerce/forsale/search?q=macbook
```

### Step 2: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Blocket"
4. Paste your search URL
5. Give it a name (e.g. "Stockholm Cars", "Cheap Laptops")
6. Set poll interval (default: 10 minutes)
7. Click **Submit**

### Step 3: Wait for First Poll

The integration will:
1. Immediately fetch current listings (this is the "seed" poll)
2. Wait 10 minutes (or your interval)
3. On the next poll, **new** listings will fire events

**Important**: No events fire on the first poll (prevents spam on setup).

## Create an Automation

### Example: Telegram Notification

```yaml
automation:
  - alias: "New Blocket Listing Alert"
    trigger:
      - platform: event
        event_type: blocket_new_listing
    action:
      - service: notify.telegram
        data:
          title: "🔔 New Blocket Listing"
          message: |
            {{ trigger.event.data.title }}
            💰 {{ trigger.event.data.price }} {{ trigger.event.data.currency }}
            🔗 {{ trigger.event.data.url }}
```

### Example: Filter by Price

```yaml
automation:
  - alias: "Cheap Car Alert"
    trigger:
      - platform: event
        event_type: blocket_new_listing
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.price < 150000 }}"
      - condition: template
        value_template: "{{ trigger.event.data.watch_name == 'Stockholm Cars' }}"
    action:
      - service: notify.mobile_app
        data:
          title: "Cheap car found!"
          message: "{{ trigger.event.data.title }} - Only {{ trigger.event.data.price }} SEK!"
```

### Example: Multiple Watches

```yaml
automation:
  - alias: "Car Alerts"
    trigger:
      - platform: event
        event_type: blocket_new_listing
        event_data:
          watch_name: "Stockholm Cars"
    action:
      - service: notify.telegram_cars
        data:
          message: "New car: {{ trigger.event.data.title }}"

  - alias: "Electronics Alerts"
    trigger:
      - platform: event
        event_type: blocket_new_listing
        event_data:
          watch_name: "Cheap Laptops"
    action:
      - service: notify.discord_tech
        data:
          message: "New laptop: {{ trigger.event.data.title }}"
```

## Check It's Working

### View Sensors

Go to **Settings** → **Devices & Services** → **Blocket** → click your watch

You'll see three sensors:
- **Last Listing**: Most recent listing title
- **New Listings**: Count from last poll
- **Last Poll**: Timestamp

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.blocket: debug
```

Restart HA, then watch logs:

```bash
tail -f home-assistant.log | grep blocket
```

You should see:

```
INFO: First poll for 'Stockholm Cars': seeded with 45 listings (no events fired)
```

After 10 minutes:

```
INFO: Found 2 new listing(s) for 'Stockholm Cars'
DEBUG: Fired event blocket_new_listing: {'source': 'blocket', ...}
```

### Listen for Events

Developer Tools → Events → Listen to event `blocket_new_listing`

Wait for the second poll (after seed), then you'll see events appear.

## Troubleshooting

### "Invalid URL" error

Make sure you're using a **search URL**, not a listing URL:

- ❌ `https://www.blocket.se/mobility/item/26688057` (listing)
- ✅ `https://www.blocket.se/mobility/search/car` (search)

### No events firing

1. **First poll doesn't fire events** (by design)
2. Wait for the second poll (10 minutes)
3. Check sensors update
4. Verify new listings exist on Blocket
5. Enable debug logging

### Integration won't load

1. Check HA version (2024.1.0+ required)
2. Restart HA after installation
3. Check logs for errors

### Need more help?

See [README.md](README.md) for full documentation or open an issue on [GitHub](https://github.com/Vortitron/ha-blocket/issues).

## Advanced: Multiple Watches

You can add multiple watches (e.g. different locations, categories):

1. Add Integration → Blocket → paste URL → name it
2. Repeat for each search you want to watch
3. Each watch has its own sensors and fires separate events

**Example setup:**

- Watch 1: "Stockholm Cars" (mobility search, Stockholm, 100k-200k SEK)
- Watch 2: "Gothenburg Apartments" (housing search, Gothenburg)
- Watch 3: "Cheap Electronics" (electronics, nationwide, max 5000 SEK)

Each fires its own `blocket_new_listing` events with `watch_name` set appropriately.

## Upstream Integration

The `blocket_new_listing` event is designed for **downstream consumers**:

- Telegram bots (e.g. Fyndbot)
- Discord webhooks
- Node-RED flows
- Custom scripts
- Vome automations

The event schema is stable and documented. Build whatever you want on top of it!

---

**Enjoy! 🎉**

*This is an unofficial integration, not affiliated with Blocket AB or Schibsted.*
