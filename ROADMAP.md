# Roadmap

## Done

- **v1.2** — LAN supervision of the desktop apps via morfBeacon heartbeats,
  two-column status area (up to 6 items), and self-monitoring of the dashboard
  service.
- **v1.1** — ST7789 support alongside ILI9341, embedded DejaVu Sans Mono font,
  unexpected-reboot badge.
- **v1.0.1** — version from the `VERSION` file, health dots (CPU/RAM/Swap/SSD/
  Load), SSD used/total, load as a percentage of cores, configurable services.

## Planned

- GPU temperature.
- Wi-Fi RSSI (signal strength).
- Automatic screen rotation.
- Alert notifications.
- **`beacon_status.py`** — a small SSH-run CLI to fetch a desktop app's detailed
  `/status` metrics on demand (the headless screen only shows presence).
