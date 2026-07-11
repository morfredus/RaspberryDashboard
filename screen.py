
"""
screen.py
Sélection du pilote d'écran selon la configuration.

Le reste du projet importe « Display » depuis ce module et ignore
quel pilote matériel (ILI9341 ou ST7789) est réellement utilisé.
"""

from config import DISPLAY_DRIVER

if DISPLAY_DRIVER == "st7789":
    from st7789 import Display
elif DISPLAY_DRIVER == "ili9341":
    from ili9341 import Display
else:
    raise ValueError(
        f"DISPLAY_DRIVER inconnu : {DISPLAY_DRIVER!r} "
        "(valeurs possibles : 'ili9341', 'st7789')"
    )

__all__ = ["Display"]
