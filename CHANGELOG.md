# CHANGELOG

## v1.1.0

### Matériel

-   Prise en charge de l'écran **ST7789** (240 × 320 SPI) en plus de
    l'ILI9341. Le pilote est choisi via `DISPLAY_DRIVER` dans `config.py`
    (`"ili9341"` ou `"st7789"`).
-   Nouveau pilote `st7789.py` exposant la même API `Display`.
-   Nouveau module `screen.py` : sélectionne le pilote selon la
    configuration ; `dashboard.py` et `boot.py` importent `Display` depuis
    ce module (plus de dépendance directe à un pilote).
-   Décalages de dalle `ST7789_X_OFFSET` / `ST7789_Y_OFFSET` dans
    `config.py` pour les panneaux nécessitant un offset.

### Interface

-   Police **DejaVu Sans Mono** (fournie dans `assets/fonts/`) à la place
    de la police bitmap PIL par défaut : texte net et anti-crénelé sur les
    deux écrans, colonnes parfaitement alignées.
-   Tailles de police centralisées dans `config.py` (`FONT_SIZE`,
    `TITLE_FONT_SIZE`) via l'aide `load_font()` (repli automatique sur la
    police par défaut si le fichier est absent).
-   Bandeau supérieur robuste : nom d'hôte et heure alignés dynamiquement ;
    la version centrée s'efface si le nom d'hôte est trop long (plus de
    chevauchement).
-   Badge `REBOOT!` sur la ligne `Uptime` lorsqu'un rapport `Boot_*` récent
    indique un reboot non demandé lié au démarrage courant.

### Exploitation

-   Nouveau module `reboot_alert.py` pour détecter les rapports de reboot dans
    le dossier de logs configuré et ignorer l'historique ancien.
-   Nouveau script `reboot_ack.py` pour acquitter le badge `REBOOT!` sans
    supprimer les logs.
-   Documentation du lanceur `~/bin/reboot-ack` pour appeler l'acquittement
    depuis n'importe quel dossier.

## v1.0.1

### Corrections

-   Correction du plantage au démarrage sous Raspberry Pi OS / `lgpio`
    (« GPIO not allocated ») : le chip-select (CE0 / GPIO 8) est désormais
    géré **en matériel** par le pilote SPI, et non plus piloté à la main.

### Interface

-   Affichage de la version (lue dans le fichier `VERSION`) dans le bandeau
    supérieur ; `dev` si le fichier est absent.
-   Pastilles de santé (vert / orange / rouge) devant CPU, RAM, Swap, SSD
    et sur la charge système ; température colorée selon ses seuils.
-   Colonnes réalignées pour une lecture immédiate.
-   Ligne SSD : espace utilisé / capacité totale (ex. `8 / 98 Gio`) en plus
    du pourcentage d'occupation.
-   Ligne Load : pastille de santé + charge en % des cœurs, en plus des
    moyennes 1 / 5 / 15 min.

### Configuration

-   Seuils d'alerte centralisés dans `config.py`
    (CPU, RAM, Swap, Temp, SSD, Load).
-   Fonction unique `health_color(value, warning, critical)`.
-   Liste des services surveillés pilotée par `SERVICE_LABELS` dans
    `config.py` (clé = unité systemd, valeur = libellé affiché).

## v1.0.0

-   Première architecture modulaire.
-   Séparation en modules : `config.py`, `systeminfo.py`, `display.py`,
    `boot.py`, `ili9341.py`, `dashboard.py`.
-   Animation de démarrage.
-   Affichage CPU, RAM, Swap, SSD, réseau, services.
-   Service `systemd`.
-   Démarrage automatique au boot.
