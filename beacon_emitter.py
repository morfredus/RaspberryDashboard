"""
beacon_emitter.py
Annonce la presence du dashboard sur le reseau local (protocole morfbeacon/1) et
sert un /status minimal.

Le dashboard etait le seul service du parc a n'exister que comme CONSOMMATEUR :
il ecoute les beacons des autres (beacon_listener.py) et affiche leur etat sur
l'ecran OLED, mais ne s'annoncait pas lui-meme. Il restait donc invisible dans
l'onglet Ecosysteme de morfMonitor -- jamais en panne, jamais decouvert.

Deux briques, parce que le protocole l'exige : « push presence, pull detail ».
Le heartbeat annonce un status_port ; ce port DOIT repondre, sinon l'annonce
promet un detail qui n'existe pas. On sert donc aussi un /status en lecture
seule.

Quatrieme implementation du meme contrat, apres la bibliotheque Qt (morfBeacon),
l'emetteur ESP32 (arduino/) et le C++ de morfSync. Le contrat, c'est le
protocole, pas la bibliotheque : ce module se valide comme les autres, avec
morfBeacon/tools/check-protocol.py, sur ce qui passe reellement sur le reseau.

Aucune dependance externe (bibliotheque standard uniquement).
"""

import json
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Le nom ANNONCE sur le reseau, coherent avec le reste du parc (morfSync,
# morfMonitor...) et avec l'unite systemd « morfdashboard ». Le depot garde son
# nom historique RaspberryDashboard ; c'est l'identite reseau qui compte ici,
# et morfMonitor affiche ce nom tel qu'il est annonce.
APP_NAME = "morfDashboard"
PROTO = "morfbeacon/1"


def _hostname():
    """Nom court de la machine, ou 'unknown'. Le nom pleinement qualifie
    n'apporte rien sur un LAN, ou le nom court identifie deja le Pi."""
    try:
        name = socket.gethostname()
    except OSError:
        return "unknown"
    return name.split(".", 1)[0] if name else "unknown"


class Beacon:
    """Emetteur de presence + serveur /status.

    Demarre deux threads demon : l'un diffuse le heartbeat, l'autre sert /status.
    Idempotent : un second start() ne fait rien.
    """

    def __init__(self, version, http_port, udp_port=45454, interval_s=15):
        self._version = version
        self._http_port = http_port
        self._udp_port = udp_port
        self._interval_s = interval_s
        self._instance = f"{APP_NAME}@{_hostname()}:{http_port}"
        self._started_at = time.time()
        self._udp_thread = None
        self._http_server = None
        self._http_thread = None

    # -- Corps commun aux deux documents --------------------------------------

    def _uptime_s(self):
        # L'horloge peut reculer (NTP) : jamais negatif.
        return max(0, int(time.time() - self._started_at))

    def _identity(self):
        """Champs communs au heartbeat et a /status. Construits une seule fois
        ici pour que les deux documents ne divergent pas sur l'identite."""
        return {
            "app": APP_NAME,
            "host": _hostname(),
            "version": self._version,
            "instance": self._instance,
            "state": "ok",
            "status_port": self._http_port,
            "uptime_s": self._uptime_s(),
        }

    def _heartbeat(self):
        # « proto » = protocole de TRANSPORT dans le heartbeat. Le datagramme
        # reste court (< 512 octets) : le detail vit derriere /status.
        o = {"proto": PROTO, "ts": int(time.time())}
        o.update(self._identity())
        return json.dumps(o, separators=(",", ":"))

    def _status(self):
        # Sur /status, « proto » nomme la version de CE document, pas le
        # transport -- convention du parc (morfMonitor sert « morfmonitor/1 »).
        o = dict(self._identity())
        o["proto"] = "morfdashboard/1"
        o["metrics"] = {"uptime_s": self._uptime_s()}
        return json.dumps(o)

    # -- Emission UDP ---------------------------------------------------------

    def _emit_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except OSError:
            # Sans broadcast, pas d'annonce possible : le dashboard continue
            # d'afficher. Etre decouvrable est un confort, afficher est la
            # mission -- on ne troque pas une gene contre une panne.
            sock.close()
            return
        while True:
            payload = self._heartbeat().encode("utf-8")
            try:
                sock.sendto(payload, ("255.255.255.255", self._udp_port))
            except OSError:
                pass  # interface momentanement absente : on reessaie au tour suivant
            time.sleep(self._interval_s)

    # -- Serveur /status ------------------------------------------------------

    def _make_handler(self):
        beacon = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path.rstrip("/") in ("", "/status"):
                    body = beacon._status().encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_error(404, "not found")

            def log_message(self, *args):
                pass  # pas de bruit sur stderr : ce n'est pas un serveur web general

        return Handler

    def _serve(self):
        try:
            self._http_server = ThreadingHTTPServer(("0.0.0.0", self._http_port),
                                                    self._make_handler())
        except OSError:
            # Port occupe : on renonce a /status. Le heartbeat annoncera quand
            # meme le port, mais sans reponse -- aussi, si /status ne peut pas
            # demarrer, on n'emet pas non plus (voir start()).
            self._http_server = None
            return
        self._http_server.serve_forever()

    # -- Cycle de vie ---------------------------------------------------------

    def start(self):
        if self._http_thread is not None:
            return

        # /status d'abord : un heartbeat qui annonce un port muet promet un
        # detail introuvable. Si le serveur ne demarre pas, on n'annonce pas.
        self._http_thread = threading.Thread(target=self._serve, name="beacon-status",
                                             daemon=True)
        self._http_thread.start()
        time.sleep(0.2)  # laisse _serve() tenter le bind avant de decider
        if self._http_server is None:
            return

        self._udp_thread = threading.Thread(target=self._emit_loop, name="beacon-emit",
                                            daemon=True)
        self._udp_thread.start()


# --- Singleton pratique -------------------------------------------------------
# dashboard.py le demarre au boot, a cote de start_beacon() (l'ecouteur).

_beacon = None


def start(version, http_port, udp_port=45454, interval_s=15):
    """Demarre l'annonce de presence (idempotent). A appeler une fois au boot."""
    global _beacon
    if _beacon is None:
        _beacon = Beacon(version, http_port, udp_port, interval_s)
        _beacon.start()
    return _beacon
