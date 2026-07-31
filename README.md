# Alert RCB for Home Assistant

[![Validate](https://github.com/MatissowyMati/home-assistant-rso/actions/workflows/validate.yml/badge.svg)](https://github.com/MatissowyMati/home-assistant-rso/actions/workflows/validate.yml)
[![GitHub release](https://img.shields.io/github/v/release/MatissowyMati/home-assistant-rso)](https://github.com/MatissowyMati/home-assistant-rso/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![HACS: Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)

**Alert RCB** is a modern Home Assistant integration for Poland's public
Regionalny System Ostrzegania warning feed. It continuously monitors official
RSO messages and makes them available to dashboards, calendars, automations,
and mobile notifications without conflicting with integrations named RSO.

The integration uses the public JSON interface documented by
[TVP's RSO integration guide](https://komunikaty.tvp.pl/Info/Integration).

## Features

| Capability | Description |
| --- | --- |
| Fast polling | Checks RSO every minute by default; configurable from 1 to 1440 minutes during setup or later. |
| Regional filtering | Monitor all of Poland or a selected voivodeship. |
| Category filtering | All, general, meteorological, hydrological, road, or water-level messages. |
| Immediate events | Emits an event entity update and `alert_rcb_new_alert` / `alert_rcb_updated_alert` bus events. |
| Notifications | Optional persistent notifications for critical alerts or every feed update. |
| Live calendar | Displays alert validity periods in a Home Assistant calendar. |
| Dashboard entities | Active-alert count, latest alert, critical-alert binary sensor, and manual refresh button. |
| Complete metadata | Includes alert text, validity, alarm level, provinces, coordinates, river and water-level data when supplied by RSO. |
| Reliable deduplication | Remembers delivered alert revisions across Home Assistant restarts. |
| Localized UI | English and Polish configuration and entity names. |
| Diagnostics | Downloadable integration diagnostics for troubleshooting. |

## Entities

Each configured feed creates:

- `sensor.*_active_alerts` — number of currently valid alerts, with a compact
  feed summary in its attributes.
- `sensor.*_latest_alert` — newest alert with its full normalized payload.
- `binary_sensor.*_critical_alert` — on when an active alert is marked by RSO
  for alarm distribution.
- `event.*_alert_event` — fires `new_alert` or `updated_alert` immediately after
  a poll detects a change.
- `calendar.*_alerts` — alert validity windows for calendar cards and triggers.
- `button.*_refresh_feed` — requests an immediate refresh.

## Installation

### HACS custom repository

1. Open **HACS → Integrations**.
2. Open the menu and select **Custom repositories**.
3. Add `https://github.com/MatissowyMati/home-assistant-rso` with category
   **Integration**.
4. Install **Alert RCB**.
5. Restart Home Assistant.

### Manual installation

Copy `custom_components/alert_rcb` into the `custom_components` directory under
your Home Assistant configuration directory, then restart Home Assistant.

## Configuration

1. Open **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **Alert RCB**.
4. Choose a feed name, province, category, polling interval, and notification
   mode.

Add multiple integration entries to monitor different province/category
combinations. Select **Configure** on an existing entry to change its polling
interval or notification mode.

Notification modes:

- `none` — no built-in persistent notifications.
- `critical` — notify only for messages marked by RSO for alarm distribution
  (default).
- `all` — notify for every new or updated message.

Existing feed items are recorded during initial setup and are not announced as
new. Later revisions of an existing message produce an `updated_alert` event.

## Fast mobile notifications

Replace `notify.mobile_app_your_phone` with the notify action for your Home
Assistant Companion App device:

```yaml
automation:
  - alias: "Alert RCB critical mobile alert"
    mode: queued
    triggers:
      - trigger: state
        entity_id: event.alert_rcb_alert_event
    conditions:
      - condition: template
        value_template: >-
          {{ trigger.to_state.attributes.critical | default(false) }}
    actions:
      - action: notify.mobile_app_your_phone
        data:
          title: "Alert RCB: {{ trigger.to_state.attributes.title }}"
          message: "{{ trigger.to_state.attributes.summary }}"
          data:
            url: "{{ trigger.to_state.attributes.url }}"
            tag: "alert-rcb-{{ trigger.to_state.attributes.id }}"
            ttl: 0
            priority: high
```

Automations can also trigger directly on the Home Assistant event bus:

```yaml
triggers:
  - trigger: event
    event_type: alert_rcb_new_alert
```

Both bus events contain the normalized alert payload:

- `id`, `title`, `summary`, and `description`
- `alarm_level` and `critical`
- `valid_from`, `valid_to`, `created_at`, and `updated_at`
- `provinces` and `category`
- `latitude`, `longitude`, `location_name`, and `river_name`
- `water_level` and `url`

## Data source and limitations

The public endpoint returns the newest page of up to 20 messages for the
selected province and category. Reading that page minimizes traffic while
providing the lowest practical notification latency.

RSO also advertises CAP/OpenAPI access, but TVP requires an administrator-issued
access token. This integration therefore uses the documented public JSON feed
and does not request or store RSO credentials.

The integration uses the logo from the
[official RSO application](https://apps.apple.com/pl/app/regionalny-system-ostrzegania/id1326612339).
The Home Assistant service device is identified as **Alert RCB**, manufactured
by **MatissowyMati**, and its configuration link points to this GitHub
repository.

> [!IMPORTANT]
> This community project is not affiliated with or endorsed by TVP or Polish
> public authorities. Home Assistant, the network, and the upstream service can
> delay or lose messages. Do not use this integration as your only source of
> emergency information.

## Development

```bash
python -m pip install ruff pytest aiohttp
ruff check .
ruff format --check .
pytest
python -m compileall custom_components
```

GitHub Actions also run Ruff, unit tests, Hassfest, and HACS validation.

## Contributing

Bug reports and pull requests are welcome. Include Home Assistant logs and the
downloaded integration diagnostics when reporting feed or parsing problems.

## License

Released under the [MIT License](LICENSE).
