
"""
dashboard.py
Point d'entrée du Dashboard Raspberry.
"""

import time

from boot import BootScreen
from display import DashboardDisplay
from screen import Display
from systeminfo import get_system_info
from beacon_listener import start as start_beacon
from config import UPDATE_INTERVAL


def main():

    lcd = Display()
    ui = DashboardDisplay()

    # Ecoute des heartbeats morfBeacon (ComponentHub, SiteWatch, futurs outils)
    # en tache de fond, des le demarrage : la presence est prete des le 1er rendu.
    start_beacon()

    try:
        # Animation de démarrage
        BootScreen().play(lcd)

        # Boucle principale
        while True:

            info = get_system_info()

            image = ui.render(info)

            lcd.display_image(image)

            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("Arrêt demandé.")

    finally:
        lcd.clear("black")
        lcd.close()


if __name__ == "__main__":
    main()
