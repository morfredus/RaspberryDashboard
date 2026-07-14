
"""
activity.py
Détection d'activité locale pour piloter la mise en veille du dashboard.

Sans capteur physique, la « présence » est déduite de l'activité des
pseudo-terminaux (/dev/pts/*). Sur un Raspberry sans écran/clavier local, ces
terminaux correspondent aux sessions SSH (et à tmux/screen ouverts dedans).
On relève le mtime le plus récent : taper une commande ou en recevoir la sortie
le rafraîchit, exactement ce que mesure la colonne IDLE de la commande « w ».

Cette approche ne dépend pas du champ « host » d'utmp (parfois vide selon la
configuration SSH), contrairement à psutil.users() : elle est donc plus fiable.
"""

import os
import time

_PTS_DIR = "/dev/pts"


def last_terminal_activity():
    """Timestamp (epoch) de la dernière activité sur un pseudo-terminal.

    Renvoie le mtime le plus récent parmi les /dev/pts/*, ou 0.0 si aucun
    terminal n'est ouvert (aucune session SSH).
    """
    latest = 0.0
    try:
        names = os.listdir(_PTS_DIR)
    except OSError:
        return 0.0

    for name in names:
        if not name.isdigit():          # ignore 'ptmx' et entrées non numériques
            continue
        try:
            latest = max(latest, os.stat(f"{_PTS_DIR}/{name}").st_mtime)
        except OSError:
            continue

    return latest


if __name__ == "__main__":
    ts = last_terminal_activity()
    if ts <= 0.0:
        print("Aucune session SSH ouverte (aucun /dev/pts actif).")
    else:
        print(f"Dernière activité SSH il y a {time.time() - ts:.1f} s")
