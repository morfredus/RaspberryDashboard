# INSTALL.md

# RaspberryDashboard - Installation

Ce document décrit la mise en place de RaspberryDashboard en tant que
service systemd afin qu'il démarre automatiquement au démarrage du
Raspberry Pi.

## Prérequis

-   Debian 13 (Trixie)
-   Python 3
-   SPI activé
-   Projet installé dans :

``` text
/home/morfredus/Codage/Python/RaspberryDashboard
```

## Vérifier le fonctionnement

``` bash
cd ~/Codage/Python/RaspberryDashboard
python3 dashboard.py
```

## Installer le service

``` bash
sudo cp dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable dashboard
sudo systemctl start dashboard
```

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
