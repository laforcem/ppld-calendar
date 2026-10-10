# ppld-calendar

Mirrors Pikes Peak Library District checkout due dates into a dedicated CalDAV (Fastmail) calendar as all-day events with a 09:00 reminder the day before.

- Logs in to PPLD's Vega patron API (undocumented; may change without notice), reads checkouts, and syncs one event per item.
- Only touches calendar objects named `ppld-*.ics`. Fails closed: any login, fetch, or parse failure changes nothing.
- Checkouts only. Holds are fetched and their field names logged, but no hold events are created yet.
- Python 3 standard library only.

## Configuration (environment)

| Variable | Purpose |
|---|---|
| `PPLD_CARD_NUMBER`, `PPLD_PIN` | Library card login |
| `CALDAV_USERNAME`, `CALDAV_APP_PASSWORD` | CalDAV credentials (Fastmail app password with Calendars access) |
| `CALDAV_CALENDAR_URL` | Full CalDAV collection URL of the target calendar (https, no query string, no `//` in the path; validated at startup) |
| `HEALTHCHECK_URL` | healthchecks.io ping URL; `/fail` is appended on failure |
| `SYNC_CRON` | Cron schedule for the container, e.g. `0 6 * * *` |
| `DRY_RUN` | Set to `1` to log intended changes without writing |
| `TZ` | Container timezone (due dates are interpreted in America/Denver) |

## Develop

```
python3 -W error -m unittest discover -s tests -v
```

## Release

Pushing a tag `vX.Y.Z` runs the tests and publishes `ghcr.io/laforcem/ppld-calendar:vX.Y.Z`. The container runs one sync at start, then on `SYNC_CRON`.

Deployment config (compose, secrets mapping) lives in the [homelab](https://github.com/laforcem/homelab) repo.
