# HARDWARE

## Raspberry Pi

-   Raspberry Pi 4
-   Debian 13 (Trixie)

## Écran

-   ILI9341 **ou** ST7789 SPI
-   240 × 320 pixels

Le pilote est sélectionné par `DISPLAY_DRIVER` dans `config.py`
(`"ili9341"` ou `"st7789"`). Le brochage, le bus SPI et la vitesse sont
communs aux deux écrans. Les dalles ST7789 240 × 240 peuvent nécessiter un
décalage (`ST7789_X_OFFSET` / `ST7789_Y_OFFSET`).

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
