
"""
boot.py
Animation de démarrage du Dashboard Raspberry.
"""

import time

from PIL import Image, ImageDraw

from config import WIDTH, HEIGHT, LOGO_FILE, FONT_ANTIALIAS, load_font


class BootScreen:

    def __init__(self):
        self.font = load_font()

    def _frame(self, percent: int):

        img = Image.new("RGB", (WIDTH, HEIGHT), "black")
        draw = ImageDraw.Draw(img)
        draw.fontmode = "L" if FONT_ANTIALIAS else "1"

        # Logo
        try:
            logo = Image.open(LOGO_FILE).convert("RGBA")
            logo.thumbnail((140, 140))
            x = (WIDTH - logo.width) // 2
            img.paste(logo, (x, 25), logo)
        except Exception:
            draw.text((70, 60), "Dashboard", fill="white", font=self.font)

        draw.text((60, 185), "Initialisation...", fill="white", font=self.font)

        # Barre
        x0 = 25
        y0 = 215
        w = WIDTH - 50
        h = 18

        draw.rectangle((x0, y0, x0 + w, y0 + h), outline="white")

        fill = int((w - 2) * percent / 100)

        if fill > 0:
            draw.rectangle(
                (x0 + 1, y0 + 1, x0 + fill, y0 + h - 1),
                fill="#00C853"
            )

        txt = f"{percent} %"
        tw = draw.textlength(txt, font=self.font)
        draw.text(((WIDTH - tw) / 2, 245), txt, fill="white", font=self.font)

        return img

    def play(self, display):

        for p in (0, 10, 20, 35, 50, 65, 80, 90, 100):
            display.display_image(self._frame(p))
            time.sleep(0.18)


if __name__ == "__main__":

    from screen import Display

    lcd = Display()

    try:
        BootScreen().play(lcd)
    finally:
        lcd.close()
