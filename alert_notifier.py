"""
Alertes persistantes du dashboard.

Le dashboard decide quand une vraie alerte existe. morfNotify ne sert qu'a
distribuer le message vers ses destinations configurees (email, log, webhook...).
Si morfNotify est absent ou lent, l'erreur est ignoree.
"""

import json
import threading
import time
import urllib.request

from config import (
    ALERT_NOTIFY_ENABLED,
    ALERT_NOTIFY_URL,
    ALERT_NOTIFY_TARGETS,
    ALERT_NOTIFY_TIMEOUT,
    ALERT_MIN_DURATION_SECONDS,
    ALERT_SERVICE_MIN_DURATION_SECONDS,
    ALERT_REPEAT_COOLDOWN_SECONDS,
    ALERT_RECOVERY_NOTIFY,
    SERVICE_LABELS,
    RED,
    CPU_CRITICAL,
    RAM_CRITICAL,
    SWAP_CRITICAL,
    SSD_CRITICAL,
    TEMP_CRITICAL,
    LOAD_CRITICAL,
)


class AlertNotifier:
    def __init__(self):
        self._states = {}

    def process(self, info):
        if not ALERT_NOTIFY_ENABLED:
            return

        now = time.time()
        active = self._active_conditions(info)
        active_keys = set(active)

        for key, alert in active.items():
            state = self._states.setdefault(key, {
                "since": now,
                "sent_at": 0,
                "active": False,
                "summary": alert["summary"],
            })
            state["summary"] = alert["summary"]
            duration = now - state["since"]
            min_duration = alert["min_duration"]
            cooldown_done = now - state["sent_at"] >= ALERT_REPEAT_COOLDOWN_SECONDS

            if duration >= min_duration and (not state["active"] or cooldown_done):
                self._send(alert["title"], alert["message"], alert["level"])
                state["sent_at"] = now
                state["active"] = True

        for key in list(self._states):
            if key in active_keys:
                continue

            state = self._states.pop(key)
            if ALERT_RECOVERY_NOTIFY and state.get("active"):
                self._send(
                    "RaspberryDashboard",
                    f"Retour a la normale : {state.get('summary', key)}",
                    "success",
                )

    def _active_conditions(self, info):
        alerts = {}
        self._add_metric(alerts, "cpu", "CPU", info.get("cpu"), CPU_CRITICAL, "%")
        self._add_metric(alerts, "ram", "RAM", info.get("ram_percent"), RAM_CRITICAL, "%")
        self._add_metric(alerts, "swap", "Swap", info.get("swap_percent"), SWAP_CRITICAL, "%")
        self._add_metric(alerts, "disk", "Disque", info.get("disk_percent"), SSD_CRITICAL, "%")
        self._add_metric(alerts, "temp", "Temperature", info.get("temp"), TEMP_CRITICAL, " C")

        load = info.get("load")
        cores = info.get("cpu_cores", 1) or 1
        if load:
            self._add_metric(alerts, "load", "Charge", load[0] / cores * 100, LOAD_CRITICAL, "% des coeurs")

        dashboard_label = SERVICE_LABELS.get("morfdashboard")
        for service in info.get("services", []):
            label = service.get("label", "service")
            if label == dashboard_label:
                continue
            if service.get("color") == RED:
                key = f"service:{label}"
                summary = f"{label} defaillant"
                alerts[key] = {
                    "title": "RaspberryDashboard",
                    "summary": summary,
                    "message": f"Alerte persistante : {summary}. Le service ou l'application reste hors ligne.",
                    "level": "error",
                    "min_duration": ALERT_SERVICE_MIN_DURATION_SECONDS,
                }

        reboot_alert = info.get("reboot_alert", {})
        if reboot_alert.get("active"):
            latest = reboot_alert.get("latest") or "rapport inconnu"
            alerts["reboot"] = {
                "title": "RaspberryDashboard",
                "summary": "reboot non demande detecte",
                "message": f"Reboot non demande detecte. Rapport : {latest}",
                "level": "warning",
                "min_duration": 0,
            }

        return alerts

    def _add_metric(self, alerts, key, label, value, critical, unit):
        if value is None or value < critical:
            return

        display_value = f"{value:.1f}{unit}" if isinstance(value, float) else f"{value}{unit}"
        summary = f"{label} critique ({display_value})"
        alerts[f"metric:{key}"] = {
            "title": "RaspberryDashboard",
            "summary": summary,
            "message": (
                f"Alerte persistante : {summary}. "
                f"Seuil critique : {critical}{unit}."
            ),
            "level": "error",
            "min_duration": ALERT_MIN_DURATION_SECONDS,
        }

    def _send(self, title, message, level):
        if not ALERT_NOTIFY_TARGETS:
            return

        payload = {
            "title": title,
            "message": message,
            "level": level,
            "targets": ALERT_NOTIFY_TARGETS,
        }
        thread = threading.Thread(target=self._post, args=(payload,), daemon=True)
        thread.start()

    def _post(self, payload):
        try:
            body = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                ALERT_NOTIFY_URL,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=ALERT_NOTIFY_TIMEOUT):
                pass
        except Exception:
            pass
