# Changelog

All notable changes to the project are recorded in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and the project follows [Semantic Versioning](https://semver.org/) (the `VERSION`
file at the repository root).

## [1.6.1] — 2026-07-15

### Changed — systemd unit renamed to `morfdashboard`

- The systemd service is now named **`morfdashboard`** (was `dashboard`), for
  ecosystem consistency. Updated: the unit file (`scripts/linux/morfdashboard.service`),
  the install/update scripts, the monitored-service key in `config.py`
  (`SERVICE_LABELS`) and its exclusion in `systeminfo.py` (so the dashboard keeps
  showing its own status correctly), and `docs/fr/INSTALL.md`.
- The **old `dashboard` service must be removed manually** before/after
  installing the new one (see chat / project notes).

## [1.6.0] — 2026-07-15

### Added — robust systemd install

- **`scripts/linux/install-service.sh`** installs the app into a **fixed location**
  (`/opt/morfdashboard`), independent of where the git clone lives. Moving or
  renaming the repository (or a Syncthing sync) no longer breaks the service. The
  script stops any previous `dashboard` service, copies the app, installs the unit
  (running as the current user, pointing at the fixed dir), enables and starts it,
  and flags any leftover autostart (crontab, `rc.local`, desktop autostart).
- **`scripts/linux/update-service.sh`**: `git pull`, re-copy to the fixed dir,
  restart — no compilation (Python).
- The unit name stays **`dashboard`** (the one the dashboard monitors).

### Changed

- Removed the repository-root `dashboard.service` with its hardcoded path (the
  source of the fragility). The parametrized unit now lives in `scripts/linux/`.

## [1.5.0] — 2026-07-14

### Added — standby (screensaver) mode

An anti-burn-in / power-saving standby screen that takes over from the dashboard
after a period of inactivity, with **software presence** detection (no sensor
yet). Numbered summary of the changes:

1. **Standby triggered by SSH inactivity.** After `SCREENSAVER_IDLE_SECONDS`
   (60 s) with no SSH terminal activity, the display switches to a minimal
   standby frame; any SSH activity wakes it immediately. Disable globally with
   `SCREENSAVER_ENABLED = False`. A start-up grace keeps the dashboard visible
   right after boot (no immediate standby when no one is connected yet).
2. **Presence from SSH activity (`activity.py`).** New module reading the most
   recent mtime of the `/dev/pts/*` pseudo-terminals — the same signal as the
   `IDLE` column of `w`. It does not depend on the utmp `host` field (sometimes
   empty), which makes detection reliable.
3. **Backlight dimming (software PWM).** `st7789.py` / `ili9341.py` now expose
   `set_backlight(0-100)` driven by PWM on `LED_PIN` (GPIO 18): the standby
   screen drops to `SCREENSAVER_BACKLIGHT` (15 %) and returns to `BACKLIGHT_FULL`
   when active. New `config.py` keys `BACKLIGHT_PWM`, `BACKLIGHT_FREQ_HZ`,
   `BACKLIGHT_FULL`; set `BACKLIGHT_PWM = False` for an on/off backlight.
4. **Three status dots on the standby frame (`systeminfo.screensaver_status`).**
   A row of three dots summarizing, left to right: **G** global/thermal
   (green/orange/red against `TEMP_*`), **P** CPU load on **4 levels**
   (green < `CPU_ELEVATED` 50 % · yellow · orange ≥ `CPU_WARNING` · red ≥
   `CPU_CRITICAL`), **S** services (green if all up, orange if at least one is
   down — never red; the `dashboard` service is excluded from the test since it
   is necessarily running). New threshold `CPU_ELEVATED` in `config.py`.
5. **Standby-frame legibility.** A letter (**G / P / S**) is drawn above each dot
   in an intermediate font size and in the uptime colour; the clock is softened
   (grey instead of pure white) and the uptime is slightly enlarged. The frame
   is repositioned at every refresh to avoid fixing the same pixels.
6. **`overall_status()` helper** in `systeminfo.py`: a single aggregated health
   verdict (`ok` / `warning` / `critical`) over the metrics and services.

These screens are LCD panels (ST7789 / ILI9341): true permanent burn-in is an
OLED phenomenon, so here the main gain is the reduced backlight (power draw and
LED lifespan), the moving frame guarding only against transient retention.

## [1.4.0] — 2026-07-13

### Added
- **`beacon_status.py`** — an SSH-run CLI that discovers the live morfBeacon apps
  on the LAN, queries their `/status` endpoint and prints their detailed metrics,
  producing a human-friendly **Markdown report** (`beacon_status.md`). The
  headless screen only shows presence; this tool gives the detail on demand.

### Changed
- `beacon_listener.py` now sets `SO_REUSEPORT` (best-effort) so the dashboard
  service and `beacon_status.py` can listen on port `45454` at the same time.

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
