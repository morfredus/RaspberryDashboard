
"""
dashboard.py
Point d'entrée du Dashboard Raspberry.
"""

import time

from boot import BootScreen
from display import DashboardDisplay
from screensaver import ScreenSaver
from screen import Display
from systeminfo import get_system_info, screensaver_status
from activity import last_terminal_activity
from beacon_listener import start as start_beacon
from config import (
    UPDATE_INTERVAL,
    SCREENSAVER_ENABLED,
    SCREENSAVER_IDLE_SECONDS,
    SCREENSAVER_BACKLIGHT,
    BACKLIGHT_FULL,
)


def main():

    lcd = Display()
    ui = DashboardDisplay()
    saver = ScreenSaver()

    # Evite de renvoyer la meme consigne de luminosite a chaque tour de boucle :
    # on ne pilote le retroeclairage que lorsque le niveau change reellement.
    current_backlight = None

    def set_backlight(level):
        nonlocal current_backlight
        if level != current_backlight:
            lcd.set_backlight(level)
            current_backlight = level

    # Ecoute des heartbeats morfBeacon (ComponentHub, SiteWatch, futurs outils)
    # en tache de fond, des le demarrage : la presence est prete des le 1er rendu.
    start_beacon()

    try:
        # Animation de démarrage
        BootScreen().play(lcd)
        set_backlight(BACKLIGHT_FULL)

        # Grace au demarrage : on part comme si une activite venait d'avoir lieu,
        # pour afficher le dashboard des le boot et ne basculer en veille qu'apres
        # SCREENSAVER_IDLE_SECONDS reels sans activite SSH.
        last_active = time.time()

        # Boucle principale
        while True:

            info = get_system_info()

            # Tout mtime de pseudo-terminal plus recent que notre dernier releve
            # = quelqu'un travaille en SSH -> le systeme est actif maintenant.
            activity_ts = last_terminal_activity()
            if activity_ts > last_active:
                last_active = activity_ts

            idle = time.time() - last_active

            # Mise en veille : declenchee par l'inactivite SSH (voir activity.py).
            # Desactivable globalement via SCREENSAVER_ENABLED.
            asleep = SCREENSAVER_ENABLED and idle >= SCREENSAVER_IDLE_SECONDS

            if asleep:
                image = saver.render(info, screensaver_status(info))
                set_backlight(SCREENSAVER_BACKLIGHT)
            else:
                image = ui.render(info)
                set_backlight(BACKLIGHT_FULL)

            lcd.display_image(image)

            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print("Arrêt demandé.")

    finally:
        lcd.clear("black")
        lcd.close()


if __name__ == "__main__":
    main()
