# RaspberryDashboard

Tableau de bord système pour Raspberry Pi, affiché sur un petit écran
**ILI9341 ou ST7789 SPI (240 × 320)**. Il donne, en un coup d'œil, l'état de santé de
la machine : CPU, mémoire, disque, charge, réseau et services.

L'objectif : connaître l'état du Raspberry en moins d'une seconde, sans clavier
ni écran principal.

## Aperçu de l'affichage

    ┌────────────────────────────────────┐
    │ pi4fred          v1.0.1     13:25:59│   bandeau : hôte / version / heure
    ├────────────────────────────────────┤
    │ ● CPU    2.1 %        43.7 °C        │   pastille de santé + température
    │ ● RAM   42.9 %                       │
    │ ● Swap   2.1 %                       │
    │ ● SSD    8.7 %       8 / 98 Gio      │   % occupé + utilisé / capacité
    ├────────────────────────────────────┤
    │ ETH   192.168.1.42                   │
    │ WIFI  --                             │
    │ mDNS  pi4fred.local                  │
    ├────────────────────────────────────┤
    │ Uptime 3j 4h                         │
    │ ● Load 0.15 0.22 0.30   4 %          │   moyennes 1/5/15 min + % cœurs
    ├────────────────────────────────────┤
    │ GatewayLab                    ●      │
    │ ComponentHub                  ●      │   état des services systemd
    │ MeteoHub                      ●      │
    └────────────────────────────────────┘

Les **pastilles de santé** changent de couleur selon des seuils :

-   🟢 **Vert** : fonctionnement normal
-   🟠 **Orange** : seuil d'avertissement
-   🔴 **Rouge** : seuil critique

## Matériel

Voir [HARDWARE.md](HARDWARE.md) pour l'écran, le brochage et le SPI.

## Installation

Voir [INSTALL.md](INSTALL.md) pour l'installation en service `systemd`
(démarrage automatique au boot).

Test rapide, sans installer le service :

``` bash
cd ~/Codage/Python/RaspberryDashboard
python3 dashboard.py
```

## Configuration

Tous les réglages sont centralisés dans [config.py](config.py).

### Seuils de santé

Chaque métrique possède un seuil d'avertissement et un seuil critique :

``` python
CPU_WARNING = 70      ;  CPU_CRITICAL = 90
RAM_WARNING = 80      ;  RAM_CRITICAL = 95
SWAP_WARNING = 20     ;  SWAP_CRITICAL = 50
TEMP_WARNING = 65     ;  TEMP_CRITICAL = 75      # °C
SSD_WARNING = 85      ;  SSD_CRITICAL = 95
LOAD_WARNING = 100    ;  LOAD_CRITICAL = 150     # % des cœurs
```

`LOAD` est exprimé en pourcentage des cœurs : `100 %` = tous les cœurs
pleinement occupés.

### Services surveillés

Les services affichés sont définis dans `SERVICE_LABELS` — la **clé** est le
nom de l'unité systemd (`systemctl is-active <clé>`), la **valeur** est le
libellé affiché :

``` python
SERVICE_LABELS = {
    "gatewaylab": "GatewayLab",
    "componenthub": "ComponentHub",
    "meteohub": "MeteoHub",
}
```

Ajouter ou retirer un service ne demande de modifier que ce dictionnaire.

### Version

Le numéro affiché dans le bandeau est lu dans le fichier `VERSION` à la racine.
En son absence, `dev` est affiché.

## Documentation

-   [ARCHITECTURE.md](ARCHITECTURE.md) — structure du projet et rôle des modules
-   [HARDWARE.md](HARDWARE.md) — matériel et brochage
-   [INSTALL.md](INSTALL.md) — installation du service systemd
-   [CHANGELOG.md](CHANGELOG.md) — historique des versions
-   [ROADMAP.md](ROADMAP.md) — évolutions prévues

## Version

Voir le fichier `VERSION` et le [CHANGELOG.md](CHANGELOG.md).
