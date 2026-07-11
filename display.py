
"""
display.py
Gestion de l'affichage du Dashboard.
Aucune dépendance au matériel : uniquement Pillow.
"""

from PIL import Image, ImageDraw, ImageFont

from config import (
    WIDTH,
    HEIGHT,
    CPU_WARNING,
    CPU_CRITICAL,
    RAM_WARNING,
    RAM_CRITICAL,
    SWAP_WARNING,
    SWAP_CRITICAL,
    TEMP_WARNING,
    TEMP_CRITICAL,
    SSD_WARNING,
    SSD_CRITICAL,
    LOAD_WARNING,
    LOAD_CRITICAL,
    SERVICE_LABELS,
    health_color,
)

# Colonnes d'alignement (px) pour la zone système
DOT_X = 10          # pastille de santé
LABEL_X = 24        # début du libellé (CPU / RAM / Swap / SSD)
DETAIL_X = 112      # colonne secondaire (température, détail SSD)
SERVICE_DOT_X = 150  # pastille d'état des services


class DashboardDisplay:

    def __init__(self):
        self.font = ImageFont.load_default()
        self.title_font = ImageFont.load_default()

    def _dot(self, draw, y, color):
        draw.ellipse((DOT_X, y + 3, DOT_X + 8, y + 11), fill=color)

    def render(self, info):

        img = Image.new("RGB", (WIDTH, HEIGHT), "black")
        draw = ImageDraw.Draw(img)

        self._header(draw, info)
        self._system(draw, info)
        self._network(draw, info)
        self._runtime(draw, info)
        self._services(draw, info)

        return img

    def _header(self, draw, info):
        draw.rectangle((0, 0, WIDTH, 26), fill="#0055A5")
        draw.text((6, 7), info["hostname"], fill="white", font=self.title_font)

        version = f"v{info.get('version', 'dev')}"
        vw = draw.textlength(version, font=self.title_font)
        draw.text(((WIDTH - vw) / 2, 7), version, fill="#BBD6F2", font=self.title_font)

        draw.text((WIDTH - 58, 7), info["time"], fill="white", font=self.title_font)

    def _metric(self, draw, y, label, value, warning, critical):
        """Pastille de santé + libellé/valeur alignés. Texte toujours blanc."""
        self._dot(draw, y, health_color(value, warning, critical))
        draw.text((LABEL_X, y),
                  f"{label:<5}{value:>5.1f} %",
                  fill="white",
                  font=self.font)

    def _system(self, draw, info):
        y = 38

        # CPU + température (colonne secondaire)
        self._metric(draw, y, "CPU", info["cpu"], CPU_WARNING, CPU_CRITICAL)
        if info["temp"] is None:
            temp_txt, temp_col = "--", "gray"
        else:
            temp_txt = f"{info['temp']:.1f} °C"
            temp_col = health_color(info["temp"], TEMP_WARNING, TEMP_CRITICAL)
        draw.text((DETAIL_X, y), temp_txt, fill=temp_col, font=self.font)

        y += 20
        self._metric(draw, y, "RAM", info["ram_percent"], RAM_WARNING, RAM_CRITICAL)

        y += 20
        self._metric(draw, y, "Swap", info["swap_percent"], SWAP_WARNING, SWAP_CRITICAL)

        y += 20
        self._metric(draw, y, "SSD", info["disk_percent"], SSD_WARNING, SSD_CRITICAL)
        detail = f"{info['disk_used_gb']:.0f} / {info['disk_total_gb']:.0f} Gio"
        draw.text((DETAIL_X, y), detail, fill="gray", font=self.font)

        draw.line((10, 122, WIDTH-10, 122), fill="gray")

    def _network(self, draw, info):
        y = 132
        draw.text((10, y), f"ETH   {info['eth'] or '--'}", fill="white", font=self.font)
        y += 18
        draw.text((10, y), f"WIFI  {info['wifi'] or '--'}", fill="white", font=self.font)
        y += 18
        draw.text((10, y), f"mDNS  {info['hostname']}.local", fill="yellow", font=self.font)

        draw.line((10, 188, WIDTH-10, 188), fill="gray")

    def _runtime(self, draw, info):
        y = 198
        draw.text((10, y), f"Uptime {info['uptime']}", fill="lightgreen", font=self.font)

        y += 18
        la = info["load"]
        cores = info.get("cpu_cores", 1) or 1
        load_pct = la[0] / cores * 100  # charge 1 min rapportée au nb de cœurs

        self._dot(draw, y, health_color(load_pct, LOAD_WARNING, LOAD_CRITICAL))
        draw.text((LABEL_X, y),
                  f"{'Load':<5}{la[0]:.2f} {la[1]:.2f} {la[2]:.2f}  {load_pct:>3.0f} %",
                  fill="lightblue",
                  font=self.font)

        draw.line((10, 242, WIDTH-10, 242), fill="gray")

    def _services(self, draw, info):
        y = 252

        for service, running in info["services"].items():
            name = SERVICE_LABELS.get(service, service.capitalize())
            draw.text((10, y), name, fill="white", font=self.font)
            color = "lime" if running else "red"
            draw.ellipse((SERVICE_DOT_X, y+2, SERVICE_DOT_X+8, y+10), fill=color)
            y += 18


if __name__ == "__main__":
    from systeminfo import get_system_info

    ui = DashboardDisplay()
    img = ui.render(get_system_info())
    img.save("dashboard_preview.png")
    print("dashboard_preview.png généré.")
