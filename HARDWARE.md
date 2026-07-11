# HARDWARE

## Raspberry Pi

-   Raspberry Pi 4
-   Debian 13 (Trixie)

## Écran

-   ILI9341 SPI
-   240 × 320 pixels

## Brochage

  Signal        GPIO
  ----------- ------
  DC              24
  RESET           25
  CS               8
  Backlight       18

## SPI

-   Bus : SPI0
-   Device : 0
-   Vitesse : 40 MHz

Le CS (GPIO 8 / CE0) est piloté **automatiquement par le contrôleur SPI**,
sans gestion logicielle via `RPi.GPIO`. Le revendiquer manuellement provoque
l'erreur « GPIO not allocated » sous `lgpio`.

Les paramètres matériels sont centralisés dans `config.py`.
