# CHANGELOG

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
