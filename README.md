# Regionalny System Ostrzegania (RSO) for Home Assistant

Custom Home Assistant integration for Poland's public Regionalny System Ostrzegania feed.

## Features

- Configurable province and RSO category feeds.
- Polling every **1 minute by default**, adjustable from 1 to 1440 minutes.
- Event entity for every new or updated alert.
- Home Assistant bus events: `rso_new_alert` and `rso_updated_alert`.
- Persistent notifications for critical alerts by default; configurable to none, critical, or all.
- Calendar entity containing the current alert feed.
- Active-alert count and latest-alert sensors.
- Binary sensor indicating alerts marked for alarm distribution by RSO.
- Manual refresh button, diagnostics, Polish and English UI.
- Restart-safe deduplication, so existing alerts are not announced again after restart.

The public JSON endpoint described by [TVP's RSO integration documentation](https://komunikaty.tvp.pl/Info/Integration) is used. CAP/OpenAPI access is not included because TVP requires a separately issued access token.

## Install

### HACS

1. In HACS, open **Integrations**, then **Custom repositories**.
2. Add `https://github.com/MatissowyMati/home-assistant-rso` as an **Integration**.
3. Install **Regionalny System Ostrzegania (RSO)** and restart Home Assistant.

### Manual

Copy `custom_components/rso` into your Home Assistant `config/custom_components` directory and restart Home Assistant.

## Configure

Go to **Settings → Devices & services → Add integration**, search for **Regionalny System Ostrzegania**, and select the province and category.

Use **Configure** on the integration entry to change the polling interval or built-in persistent notification mode. Add multiple entries to monitor different province/category combinations.

## Fast mobile notifications

The event entity is the easiest automation trigger. Example:

```yaml
automation:
  - alias: "RSO mobile alert"
    triggers:
      - trigger: state
        entity_id: event.rso_alert_event
    conditions:
      - condition: template
        value_template: "{{ trigger.to_state.attributes.critical | default(false) }}"
    actions:
      - action: notify.mobile_app_your_phone
        data:
          title: "RSO: {{ trigger.to_state.attributes.title }}"
          message: "{{ trigger.to_state.attributes.summary }}"
          data:
            url: "{{ trigger.to_state.attributes.url }}"
            tag: "rso-{{ trigger.to_state.attributes.id }}"
            ttl: 0
            priority: high
```

You can also trigger directly on the `rso_new_alert` or `rso_updated_alert` event types. Each event includes the full normalized alert payload.

## Notes

- The feed is cloud-polled; the fastest supported interval is one minute.
- The integration reads the newest RSO page (up to 20 items, as documented by RSO) to minimize network traffic and notification latency.
- RSO data is published by TVP and relevant Polish public authorities. This project is not affiliated with or endorsed by TVP.

## License

MIT
