
"""
screensaver.py
Écran de veille anti-marquage / économie d'énergie.

Fond noir avec un petit cadre repositionné aléatoirement à chaque rendu, pour
ne jamais fixer les mêmes pixels. Le cadre affiche l'heure, l'uptime et une
rangée de trois pastilles d'état surmontées de leur initiale :
    G = état Global (thermique)   P = Processeur (charge CPU)   S = Services

Même principe que display.py / boot.py : rendu Pillow pur, aucun accès
matériel. Le pilotage du rétroéclairage (baisse de luminosité) est géré par
dashboard.py, pas ici. Les couleurs des pastilles sont calculées en amont
(systeminfo.screensaver_status) : ce module ne fait que les disposer.
"""

import random

from PIL import Image, ImageDraw

from config import WIDTH, HEIGHT, FONT_ANTIALIAS, load_font

# Couleurs de texte volontairement adoucies : lisibles mais peu lumineuses,
# pour ménager l'écran et les yeux en veille.
TIME_COLOR = "#B9BEC3"    # heure : gris clair (moins agressif que le blanc pur)
UPTIME_COLOR = "#AAB0B6"  # uptime + initiales des pastilles : gris un peu plus clair

# Tailles de police.
TIME_FONT_SIZE = 26       # heure
UPTIME_FONT_SIZE = 16     # uptime (un cran au-dessus du corps de texte standard)
LETTER_FONT_SIZE = 20     # initiales G/P/S : entre l'heure et l'uptime

# Dimensions du cadre mobile.
BOX_W = 152
BOX_H = 104
MARGIN = 4

# Rangée de pastilles et leurs initiales.
DOT_LABELS = ("G", "P", "S")   # Global (thermique), Processeur, Services
DOT_R = 7
DOT_GAP = 34


class ScreenSaver:

    def __init__(self):
        self.time_font = load_font(TIME_FONT_SIZE, bold=True)
        self.uptime_font = load_font(UPTIME_FONT_SIZE)
        self.letter_font = load_font(LETTER_FONT_SIZE, bold=True)

    def render(self, info, dots):
        """dots : itérable de 3 couleurs (thermique, charge CPU, services)."""
        img = Image.new("RGB", (WIDTH, HEIGHT), "black")
        draw = ImageDraw.Draw(img)
        draw.fontmode = "L" if FONT_ANTIALIAS else "1"

        x, y = self._next_position()

        # Heure, en gros, centrée.
        time_txt = info["time"]
        tw = draw.textlength(time_txt, font=self.time_font)
        draw.text((x + (BOX_W - tw) / 2, y + 4), time_txt,
                  fill=TIME_COLOR, font=self.time_font)

        # Uptime, discret, sous l'heure.
        up_txt = f"Uptime {info['uptime']}"
        uw = draw.textlength(up_txt, font=self.uptime_font)
        draw.text((x + (BOX_W - uw) / 2, y + 40), up_txt,
                  fill=UPTIME_COLOR, font=self.uptime_font)

        # Initiales + pastilles : chaque lettre est centrée au-dessus de sa
        # pastille, dans la même teinte que l'uptime.
        letters_y = y + 60
        cy = y + 90
        cx = x + BOX_W / 2
        for i, color in enumerate(dots):
            dx = cx + (i - 1) * DOT_GAP

            label = DOT_LABELS[i]
            lw = draw.textlength(label, font=self.letter_font)
            draw.text((dx - lw / 2, letters_y), label,
                      fill=UPTIME_COLOR, font=self.letter_font)

            draw.ellipse((dx - DOT_R, cy - DOT_R, dx + DOT_R, cy + DOT_R),
                         fill=color)

        return img

    def _next_position(self):
        """Position aléatoire du cadre, en le gardant entièrement visible."""
        x = random.randint(MARGIN, WIDTH - BOX_W - MARGIN)
        y = random.randint(MARGIN, HEIGHT - BOX_H - MARGIN)
        return x, y


if __name__ == "__main__":
    from systeminfo import get_system_info, screensaver_status

    info = get_system_info()
    ScreenSaver().render(info, screensaver_status(info)).save("screensaver_preview.png")
    print("screensaver_preview.png généré.")
