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
    │ Uptime 3j 4h              REBOOT!    │   si un reboot non demandé est détecté
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

### Alerte reboot non demandé

Les chemins ci-dessous correspondent à l'installation de `morfredus` sur
`pi4fred`. Pour une autre machine ou un autre utilisateur, remplacer
`/home/morfredus` par le dossier personnel concerné, par exemple
`/home/<utilisateur>`.

Si le script de surveillance des redémarrages crée un rapport dans
`/home/morfredus/Logs/`, le dashboard peut afficher un badge rouge `REBOOT!`
sur la ligne `Uptime`.

Le dashboard ne tient compte que d'un dossier `Boot_*` lié au démarrage
système en cours. Les anciens rapports restent donc archivés sans déclencher
le badge au prochain boot.

Réglages dans `config.py` :

``` python
REBOOT_ALERT_LOG_DIR = Path("/home/morfredus/Logs")
REBOOT_ALERT_PATTERNS = ("Boot_*",)
REBOOT_ALERT_BOOT_WINDOW_SECONDS = 10 * 60
REBOOT_ALERT_ACK_FILE = Path("/home/morfredus/Logs/.dashboard_reboot_ack")
```

Acquitter l'alerte sans supprimer les logs :

``` bash
cd ~/Codage/Python/RaspberryDashboard
python3 reboot_ack.py
```

L'acquittement écrit le nom du rapport courant dans
`/home/morfredus/Logs/.dashboard_reboot_ack`. Au prochain reboot non demandé,
un nouveau dossier `Boot_*` aura un nouveau nom et le badge réapparaîtra.

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
