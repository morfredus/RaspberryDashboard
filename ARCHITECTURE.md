# ARCHITECTURE

    RaspberryDashboard/
    ├── assets/
    │   ├── fonts/            (DejaVu Sans Mono)
    │   └── logo.png
    ├── VERSION
    ├── boot.py
    ├── config.py
    ├── dashboard.py
    ├── dashboard.service
    ├── display.py
    ├── screen.py
    ├── ili9341.py
    ├── st7789.py
    ├── systeminfo.py
    ├── README.md
    ├── INSTALL.md
    ├── CHANGELOG.md
    ├── ROADMAP.md
    ├── ARCHITECTURE.md
    ├── HARDWARE.md
    └── CABLAGE.md

## Modules

-   `dashboard.py` : point d'entrée.
-   `boot.py` : animation de démarrage.
-   `display.py` : composition de l'interface.
-   `systeminfo.py` : collecte des informations système.
-   `screen.py` : sélection du pilote d'écran selon `config.py`.
-   `ili9341.py` : pilote matériel ILI9341.
-   `st7789.py` : pilote matériel ST7789.
-   `config.py` : paramètres et seuils.
