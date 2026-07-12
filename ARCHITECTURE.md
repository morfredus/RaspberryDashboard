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
    ├── reboot_ack.py
    ├── reboot_alert.py
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
-   `reboot_alert.py` : détection du rapport `Boot_*` du démarrage courant
    et gestion de l'acquittement.
-   `reboot_ack.py` : commande CLI pour acquitter le badge `REBOOT!` sans
    supprimer les logs.
-   `systeminfo.py` : collecte des informations système.
-   `screen.py` : sélection du pilote d'écran selon `config.py`.
-   `ili9341.py` : pilote matériel ILI9341.
-   `st7789.py` : pilote matériel ST7789.
-   `config.py` : paramètres et seuils.
