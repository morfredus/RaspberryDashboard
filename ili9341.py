
"""
ili9341.py
Pilote ILI9341 réutilisable pour Dashboard Raspberry.
Version refactorisée : séparation entre Display (API publique)
et ILI9341 (pilote matériel).
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
    BACKLIGHT_PWM,
    BACKLIGHT_FREQ_HZ,
    BACKLIGHT_FULL,
)


class ILI9341:
    """Pilote matériel ILI9341."""

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Le CS (CE0 / GPIO 8) est géré en matériel par le driver SPI.
        # Ne pas le revendiquer ici : le noyau (spidev) le possède déjà,
        # sinon lgpio lève « GPIO not allocated » sur Bookworm.
        GPIO.setup(DC_PIN, GPIO.OUT)
        GPIO.setup(RST_PIN, GPIO.OUT)

        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.LOW)
        self._pwm = None  # objet PWM du rétroéclairage (créé après l'init dalle)

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
        time.sleep(0.05)

    def init_display(self):
        seq = [
            (0x01,None),(0x28,None),
            (0xCF,[0x00,0x83,0x30]),
            (0xED,[0x64,0x03,0x12,0x81]),
            (0xE8,[0x85,0x01,0x79]),
            (0xCB,[0x39,0x2C,0x00,0x34,0x02]),
            (0xF7,[0x20]),
            (0xEA,[0x00,0x00]),
            (0xC0,[0x26]),
            (0xC1,[0x11]),
            (0xC5,[0x35,0x3E]),
            (0xC7,[0xBE]),
            (0x36,[0x88]),
            (0x3A,[0x55]),
            (0xB1,[0x00,0x1B]),
            (0xF2,[0x08]),
            (0x26,[0x01]),
            (0x2A,[0x00,0x00,0x00,0xEF]),
            (0x2B,[0x00,0x00,0x01,0x3F]),
        ]

        for cmd,data in seq:
            self.write_cmd(cmd)
            if data is not None:
                self.write_data(data)

        self.write_cmd(0x11)
        time.sleep(0.1)
        self.write_cmd(0x29)
        time.sleep(0.05)

        self._init_backlight()

    def _init_backlight(self):
        """Allume le rétroéclairage : PWM (luminosité variable) ou tout-ou-rien."""
        if BACKLIGHT_PWM:
            self._pwm = GPIO.PWM(LED_PIN, BACKLIGHT_FREQ_HZ)
            self._pwm.start(BACKLIGHT_FULL)
        else:
            GPIO.output(LED_PIN, GPIO.HIGH)

    def set_backlight(self, level):
        """Règle la luminosité du rétroéclairage (0-100 %).

        Sans PWM, tout niveau > 0 allume à fond et 0 éteint.
        """
        level = max(0, min(100, int(level)))
        if self._pwm is not None:
            self._pwm.ChangeDutyCycle(level)
        else:
            GPIO.output(LED_PIN, GPIO.HIGH if level > 0 else GPIO.LOW)

    def display_image(self, image: Image.Image):
        img = image.convert("RGB")
        self.write_cmd(0x2C)

        GPIO.output(DC_PIN, GPIO.HIGH)

        b, g, r = img.split()

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
        if self._pwm is not None:
            self._pwm.stop()
        GPIO.output(LED_PIN, GPIO.LOW)
        self.spi.close()
        GPIO.cleanup()


class Display:
    """
    API publique du projet.

    Le reste du projet ne manipule jamais directement ILI9341.
    """

    def __init__(self):
        self.driver = ILI9341()

    def display_image(self, image):
        self.driver.display_image(image)

    def clear(self, color="black"):
        self.driver.clear(color)

    def set_backlight(self, level):
        self.driver.set_backlight(level)

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
