
"""
st7789.py
Pilote ST7789 pour Dashboard Raspberry.
Même API publique que ili9341.py (classe Display) : le reste du projet
ne manipule jamais directement le pilote matériel.
"""

from PIL import Image
import numpy as np
import spidev
import RPi.GPIO as GPIO
import time

from config import (
    DC_PIN,
    RST_PIN,
    LED_PIN,
    WIDTH,
    HEIGHT,
    SPI_BUS,
    SPI_DEVICE,
    SPI_SPEED,
    ST7789_X_OFFSET,
    ST7789_Y_OFFSET,
)


class ST7789:
    """Pilote matériel ST7789."""

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Le CS (CE0 / GPIO 8) est géré en MATÉRIEL par le driver SPI (spidev).
        # Ne pas le revendiquer ici : le noyau le possède déjà, sinon lgpio
        # lève « GPIO not allocated » sur Bookworm/Trixie.
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(RST_PIN, GPIO.OUT)

        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.LOW)

        self.spi = spidev.SpiDev()
        self.spi.open(SPI_BUS, SPI_DEVICE)
        self.spi.max_speed_hz = SPI_SPEED
        self.spi.mode = 0

        self.reset()
        self.init_display()

    def write_cmd(self, cmd):
        # CS est abaissé/relevé automatiquement par le matériel SPI (CE0).
        GPIO.output(DC_PIN, GPIO.LOW)
        self.spi.writebytes([cmd])

    def write_data(self, data):
        GPIO.output(DC_PIN, GPIO.HIGH)

        if isinstance(data, list):
            self.spi.writebytes(data)
        else:
            self.spi.writebytes([data])

    def reset(self):
        GPIO.output(RST_PIN, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(RST_PIN, GPIO.LOW)
        time.sleep(0.05)
        GPIO.output(RST_PIN, GPIO.HIGH)
        time.sleep(0.15)

    def init_display(self):
        self.write_cmd(0x01)      # SWRESET (reset logiciel)
        time.sleep(0.15)
        self.write_cmd(0x11)      # SLPOUT (sortie de veille)
        time.sleep(0.15)

        seq = [
            (0x3A, [0x55]),                               # COLMOD  : 16 bits/pixel (RGB565)
            (0x36, [0x00]),                               # MADCTL  : ordre RGB, portrait
            (0xB2, [0x0C, 0x0C, 0x00, 0x33, 0x33]),       # PORCTRL : porches
            (0xB7, [0x35]),                               # GCTRL
            (0xBB, [0x19]),                               # VCOMS
            (0xC0, [0x2C]),                               # LCMCTRL
            (0xC2, [0x01]),                               # VDVVRHEN
            (0xC3, [0x12]),                               # VRHS
            (0xC4, [0x20]),                               # VDVS
            (0xC6, [0x0F]),                               # FRCTRL2 : ~60 Hz
            (0xD0, [0xA4, 0xA1]),                         # PWCTRL1
            (0xE0, [0xD0, 0x04, 0x0D, 0x11, 0x13, 0x2B,   # PVGAMCTRL (gamma +)
                    0x3F, 0x54, 0x4C, 0x18, 0x0D, 0x0B,
                    0x1F, 0x23]),
            (0xE1, [0xD0, 0x04, 0x0C, 0x11, 0x13, 0x2C,   # NVGAMCTRL (gamma -)
                    0x3F, 0x44, 0x51, 0x2F, 0x1F, 0x1F,
                    0x20, 0x23]),
        ]

        for cmd, data in seq:
            self.write_cmd(cmd)
            self.write_data(data)

        self.write_cmd(0x21)      # INVON : inversion requise pour des couleurs correctes
        self.write_cmd(0x13)      # NORON : mode d'affichage normal
        time.sleep(0.01)
        self.write_cmd(0x29)      # DISPON : allumage de la dalle
        time.sleep(0.05)

        GPIO.output(LED_PIN, GPIO.HIGH)

    def _set_window(self, x0, y0, x1, y1):
        """Définit la fenêtre d'écriture (avec décalage éventuel de la dalle)."""
        x0 += ST7789_X_OFFSET
        x1 += ST7789_X_OFFSET
        y0 += ST7789_Y_OFFSET
        y1 += ST7789_Y_OFFSET

        self.write_cmd(0x2A)      # CASET (colonnes)
        self.write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self.write_cmd(0x2B)      # RASET (lignes)
        self.write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])

    def display_image(self, image: Image.Image):
        img = image.convert("RGB")

        self._set_window(0, 0, WIDTH - 1, HEIGHT - 1)
        self.write_cmd(0x2C)      # RAMWR

        GPIO.output(DC_PIN, GPIO.HIGH)

        # ST7789 configuré en RGB (MADCTL) : pas d'inversion des canaux.
        r, g, b = img.split()

        r = np.array(r, dtype=np.uint16) >> 3
        g = np.array(g, dtype=np.uint16) >> 2
        b = np.array(b, dtype=np.uint16) >> 3

        rgb565 = (r << 11) | (g << 5) | b

        buf = np.empty((HEIGHT, WIDTH, 2), dtype=np.uint8)
        buf[:, :, 0] = (rgb565 >> 8) & 0xFF
        buf[:, :, 1] = rgb565 & 0xFF

        self.spi.writebytes2(buf.tobytes())

    def clear(self, color="black"):
        self.display_image(Image.new("RGB", (WIDTH, HEIGHT), color))

    def close(self):
        GPIO.output(LED_PIN, GPIO.LOW)
        self.spi.close()
        GPIO.cleanup()


class Display:
    """
    API publique du projet (identique à celle de ili9341.py).

    Le reste du projet ne manipule jamais directement ST7789.
    """

    def __init__(self):
        self.driver = ST7789()

    def display_image(self, image):
        self.driver.display_image(image)

    def clear(self, color="black"):
        self.driver.clear(color)

    def close(self):
        self.driver.close()


if __name__ == "__main__":
    lcd = Display()
    lcd.clear("navy")
    time.sleep(2)
    lcd.clear("darkgreen")
    time.sleep(2)
    lcd.clear("black")
    lcd.close()
