# Changelog

All notable changes to the project are recorded in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and the project follows [Semantic Versioning](https://semver.org/) (the `VERSION`
file at the repository root).

## [1.3.0] — 2026-07-13

### Changed
- **Documentation overhaul and bilingual layout.** Following the convention of
  the other repositories, the root documents are now in **English**
  (`README.md`, `CHANGELOG.md`, `ROADMAP.md`, `CONTRIBUTING.md`); a French
  `README.fr.md` is kept for French speakers. The in-depth guides moved under
  `docs/fr/` (French, the reference language: architecture, hardware, wiring,
  install), with an English index at `docs/en/README.md`.
- **License clarified to GPL-3.0-only** (previously GPL-3.0-or-later): the full
  GNU GPL v3 text now ships in `LICENSE`.

### Added
- `CONTRIBUTING.md`.

## [1.2.1] — 2026-07-13

### Changed
- **Self-monitoring of the dashboard.** The local systemd service `dashboard` is
  now shown among the monitored items (green dot while it runs as a service), via
  `SERVICE_LABELS` → `systemctl is-active dashboard`.
- Removed `componenthub` from the ESP32 side (`SERVICE_LABELS` /
  `NETWORK_SERVICES`): ComponentHub no longer exists as an ESP32 — it is now
  monitored as a desktop app (morfBeacon heartbeat).

## [1.2.0] — 2026-07-13

### Added
- **LAN supervision of the desktop apps (morfBeacon).** The dashboard now listens
  for the UDP heartbeats broadcast by **ComponentHub**, **SiteWatch** (and future
  tools) on port `45454`, and shows whether each desktop app is online.
  *Push-presence* model: no probing, no IP to know, automatic discovery; an app
  with no heartbeat for `BEACON_OFFLINE_AFTER` seconds (60 s by default) is
  considered offline.
- New module `beacon_listener.py`: background UDP listener (standard library
  only). Watched apps configured in `BEACON_APPS` (`config.py`) — adding a future
  project is a single line.

### Changed
- **Status area laid out in two columns**: up to **6 monitored items** (systemd
  services + desktop apps), color dots kept. Names that are too long are
  abbreviated with a trailing ".".

## [1.1.0]

### Added
- **ST7789 (240 × 320 SPI) support** alongside the ILI9341. The driver is chosen
  via `DISPLAY_DRIVER` in `config.py` (`"ili9341"` or `"st7789"`).
- New driver `st7789.py` exposing the same `Display` API, and a new `screen.py`
  module that selects the driver from the configuration (`dashboard.py` and
  `boot.py` import `Display` from it, no direct dependency on a driver).
- Panel offsets `ST7789_X_OFFSET` / `ST7789_Y_OFFSET` in `config.py` for panels
  that need one.
- Embedded **DejaVu Sans Mono** font (in `assets/fonts/`) instead of the default
  PIL bitmap font: crisp, anti-aliased text on both screens, perfectly aligned
  columns. Font sizes centralized in `config.py` via `load_font()`.
- `reboot_alert.py` to detect reboot reports in the configured log folder while
  ignoring old history, and `reboot_ack.py` to acknowledge the `REBOOT!` badge
  without deleting the logs.

### Changed
- Robust header: hostname and time aligned dynamically; the centered version
  fades out when the hostname is too long (no more overlap).

## [1.0.1]

### Fixed
- **Startup crash on Raspberry Pi OS / `lgpio`** ("GPIO not allocated"): the
  chip-select (CE0 / GPIO 8) is now driven **in hardware** by the SPI driver,
  no longer toggled manually.

### Added
- Version (read from the `VERSION` file) shown in the header; `dev` when absent.
- Health dots (green / orange / red) in front of CPU, RAM, Swap, SSD and on the
  system load; temperature colored against its thresholds.
- SSD line: used space / total capacity (e.g. `8 / 98 Gio`) on top of the usage
  percentage. Load line: health dot + load as a percentage of cores, on top of
  the 1 / 5 / 15 min averages.

### Changed
- Alert thresholds centralized in `config.py` (CPU, RAM, Swap, Temp, SSD, Load),
  with a single `health_color(value, warning, critical)` helper.
- Monitored services driven by `SERVICE_LABELS` in `config.py`.

## [1.0.0]

### Added
- First modular architecture: `config.py`, `systeminfo.py`, `display.py`,
  `boot.py`, `ili9341.py`, `dashboard.py`.
- Boot animation; CPU, RAM, Swap, SSD, network and services display.
- `systemd` service with auto-start at boot.
