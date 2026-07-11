import socket
import shutil
import subprocess
from datetime import datetime

import psutil

from config import PROJECT_DIR, SERVICE_LABELS


def _read_version():
    try:
        return (PROJECT_DIR / "VERSION").read_text().strip() or "dev"
    except Exception:
        return "dev"


VERSION = _read_version()


def _get_ip(interface: str):
    try:
        result = subprocess.check_output(
            ["ip", "-4", "addr", "show", interface],
            text=True
        )

        for line in result.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                return line.split()[1].split("/")[0]

    except Exception:
        pass

    return None


def _cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(float(f.read()) / 1000, 1)
    except Exception:
        return None


def _uptime():
    try:
        with open("/proc/uptime") as f:
            seconds = float(f.readline().split()[0])

        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)

        if days:
            return f"{days}j {hours}h"

        return f"{hours}h {minutes}m"

    except Exception:
        return "?"


def _service_running(service: str):
    try:
        subprocess.check_output(
            ["systemctl", "is-active", "--quiet", service]
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_system_info():

    disk = shutil.disk_usage("/")

    return {

        "hostname": socket.gethostname(),

        "version": VERSION,

        "time": datetime.now().strftime("%H:%M:%S"),

        "eth": _get_ip("eth0"),

        "wifi": _get_ip("wlan0"),

        "cpu": psutil.cpu_percent(),

        "cpu_cores": psutil.cpu_count() or 1,

        "load": psutil.getloadavg(),

        "temp": _cpu_temp(),

        "ram_percent": psutil.virtual_memory().percent,

        "swap_percent": psutil.swap_memory().percent,

        "disk_percent": round(disk.used / disk.total * 100, 1),

        "disk_used_gb": round(disk.used / (1024**3), 1),

        "disk_free_gb": round(disk.free / (1024**3), 1),

        "disk_total_gb": round(disk.total / (1024**3), 1),

        "uptime": _uptime(),

        "services": {
            name: _service_running(name)
            for name in SERVICE_LABELS
        }
    }


if __name__ == "__main__":

    from pprint import pprint

    pprint(get_system_info())