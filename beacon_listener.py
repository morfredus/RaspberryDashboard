"""
beacon_listener.py
Ecoute passive des heartbeats morfBeacon (UDP broadcast) emis par les
applications de bureau (ComponentHub, SiteWatch, futurs outils).

Le dashboard ne sonde rien : il ECOUTE le port BEACON_PORT et tient a jour, pour
chaque application vue, la date du dernier heartbeat et son etat. Une application
est « en ligne » si son dernier heartbeat date de moins de BEACON_OFFLINE_AFTER
secondes.

Un seul ecouteur pour tout le programme, dans un thread de fond : demarre une
fois par dashboard.py via start(). Aucune dependance externe (stdlib seule).
"""

import json
import socket
import threading
import time

from config import BEACON_PORT, BEACON_OFFLINE_AFTER

_PROTO_PREFIX = "morfbeacon/"   # champ "proto" attendu, ex. "morfbeacon/1"


class BeaconListener:
    def __init__(self, port=BEACON_PORT):
        self._port = port
        self._lock = threading.Lock()
        self._seen = {}          # app -> {last, state, host, version, ip, status_port}
        self._thread = None

    def start(self):
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, name="beacon", daemon=True)
        self._thread.start()

    def _run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            # Permet a plusieurs ecouteurs (le service dashboard + l'outil
            # beacon_status.py lance en SSH) de recevoir le meme broadcast.
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except (AttributeError, OSError):
            pass  # SO_REUSEPORT indisponible (ex. Windows) : coexistence best-effort
        try:
            sock.bind(("", self._port))
        except OSError:
            # Port occupe : on renonce a l'ecoute, le dashboard fonctionne sans.
            return

        while True:
            try:
                data, addr = sock.recvfrom(2048)
            except OSError:
                continue
            try:
                msg = json.loads(data.decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                continue
            if not str(msg.get("proto", "")).startswith(_PROTO_PREFIX):
                continue
            app = msg.get("app")
            if not app:
                continue

            with self._lock:
                self._seen[app] = {
                    "last": time.monotonic(),
                    "state": msg.get("state", "ok"),
                    "host": msg.get("host"),
                    "version": msg.get("version"),
                    "ip": addr[0],
                    "status_port": int(msg.get("status_port", 0) or 0),
                }

    def status(self, app):
        """Retourne (online: bool, state: str|None) pour une application."""
        with self._lock:
            entry = self._seen.get(app)
            if not entry:
                return False, None
            online = (time.monotonic() - entry["last"]) <= BEACON_OFFLINE_AFTER
            return online, entry.get("state")

    def snapshot(self):
        """Copie {app: {...,'online':bool}} de toutes les applications vues."""
        now = time.monotonic()
        with self._lock:
            return {
                app: {**entry, "online": (now - entry["last"]) <= BEACON_OFFLINE_AFTER}
                for app, entry in self._seen.items()
            }


# --- Singleton pratique -------------------------------------------------------
# systeminfo.py interroge cet ecouteur unique ; dashboard.py le demarre au boot.

_listener = None


def start():
    """Demarre l'ecouteur unique (idempotent). A appeler une fois au demarrage."""
    global _listener
    if _listener is None:
        _listener = BeaconListener()
        _listener.start()
    return _listener


def status(app):
    """(online, state) pour 'app' ; (False, None) si l'ecouteur n'est pas demarre."""
    if _listener is None:
        return False, None
    return _listener.status(app)
