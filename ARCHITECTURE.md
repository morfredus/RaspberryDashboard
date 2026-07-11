# ARCHITECTURE

    RaspberryDashboard/
    ├── assets/
    ├── VERSION
    ├── boot.py
    ├── config.py
    ├── dashboard.py
    ├── dashboard.service
    ├── display.py
    ├── ili9341.py
    ├── systeminfo.py
    ├── INSTALL.md
    ├── CHANGELOG.md
    ├── ROADMAP.md
    ├── ARCHITECTURE.md
    └── HARDWARE.md

## Modules

-   `dashboard.py` : point d'entrée.
-   `boot.py` : animation de démarrage.
-   `display.py` : composition de l'interface.
-   `systeminfo.py` : collecte des informations système.
-   `ili9341.py` : pilote matériel.
-   `config.py` : paramètres et seuils.
