# INSTALL.md

# RaspberryDashboard - Installation

Ce document décrit la mise en place de RaspberryDashboard en tant que
service systemd afin qu'il démarre automatiquement au démarrage du
Raspberry Pi.

## Prérequis

-   Debian 13 (Trixie)
-   Python 3, avec les modules `Pillow`, `numpy`, `psutil`, `RPi.GPIO`, `spidev`
    (installés au niveau système ; `requirements.txt` est vide)
-   SPI activé

## Vérifier le fonctionnement (sans installer)

Depuis le dépôt :

``` bash
python3 dashboard.py
```

## Installer le service (recommandé)

L'installation **copie l'application dans un dossier fixe**
(`/opt/raspberrydashboard`), indépendant de l'emplacement du dépôt git. Déplacer
ou renommer le dépôt (ou une synchronisation Syncthing) ne casse donc plus le
service.

``` bash
sudo ./scripts/linux/install-service.sh
```

Le script : arrête un éventuel ancien service `dashboard`, copie l'application
dans `/opt/raspberrydashboard`, installe le service (exécuté par l'utilisateur
courant, pointant vers le dossier fixe), l'active au démarrage et le lance. Il
signale aussi tout autre lancement automatique résiduel (crontab, `rc.local`,
autostart) à retirer à la main.

> Le nom d'unité reste **`dashboard`** — c'est celui que RaspberryDashboard
> surveille (`systemctl is-active dashboard`).

### Mettre à jour

``` bash
sudo ./scripts/linux/update-service.sh
```

`git pull`, recopie de l'application dans `/opt/raspberrydashboard`, puis
redémarrage du service.

## Vérification

``` bash
systemctl status dashboard --no-pager
```

Le service doit être **active (running)**.

## Journaux

``` bash
journalctl -u dashboard -n 50 --no-pager
```

ou

``` bash
journalctl -u dashboard -f
```

## Gestion du service

Arrêter :

``` bash
sudo systemctl stop dashboard
```

Redémarrer :

``` bash
sudo systemctl restart dashboard
```

Désactiver le démarrage automatique :

``` bash
sudo systemctl disable dashboard
```

## Commande d'acquittement du badge reboot

Le script `reboot_ack.py` permet d'acquitter le badge `REBOOT!` sans supprimer
les dossiers de logs. Il peut être lancé directement depuis le dossier du
dashboard :

``` bash
cd ~/Codage/Python/RaspberryDashboard
python3 reboot_ack.py
```

Pour pouvoir l'utiliser depuis n'importe quel dossier avec la commande
`reboot-ack`, créer un petit lanceur dans `~/bin` :

``` bash
mkdir -p ~/bin
nano ~/bin/reboot-ack
```

Contenu du fichier `~/bin/reboot-ack` :

``` sh
#!/bin/sh
cd /home/morfredus/Codage/Python/RaspberryDashboard || exit 1
exec python3 reboot_ack.py "$@"
```

Adapter le chemin `/home/morfredus/Codage/Python/RaspberryDashboard` si le
projet est installé ailleurs.

Rendre le lanceur exécutable :

``` bash
chmod +x ~/bin/reboot-ack
```

Vérifier que `~/bin` est bien dans le `PATH` :

``` bash
command -v reboot-ack
```

Utilisation :

``` bash
reboot-ack
```

## Mise à jour

Après une mise à jour du code :

``` bash
cd ~/Codage/Python/RaspberryDashboard
git pull
sudo systemctl restart dashboard
```

Si `dashboard.service` a été modifié :

``` bash
sudo cp dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart dashboard
```

## Vérification finale

``` bash
sudo reboot
```

Après le redémarrage, le dashboard doit se lancer automatiquement.
