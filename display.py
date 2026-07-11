
"""
display.py
Gestion de l'affichage du Dashboard.
Aucune dépendance au matériel : uniquement Pillow.
"""

from PIL import Image, ImageDraw, ImageFont

from config import WIDTH, HEIGHT


class DashboardDisplay:

    def __init__(self):
        self.font = ImageFont.load_default()
        self.title_font = ImageFont.load_default()

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
        draw.text((WIDTH - 58, 7), info["time"], fill="white", font=self.title_font)

    def _system(self, draw, info):
        y = 38
        draw.text((10, y),     f"CPU     {info['cpu']:>5.1f} %", fill="white", font=self.font)
        temp = "--" if info["temp"] is None else f"{info['temp']:.1f} °C"
        draw.text((140, y), temp, fill="orange", font=self.font)

        y += 20
        draw.text((10, y), f"RAM     {info['ram_percent']:>5.1f} %", fill="white", font=self.font)

        y += 20
        draw.text((10, y), f"Swap    {info['swap_percent']:>5.1f} %", fill="white", font=self.font)

        y += 20
        draw.text((10, y),
                  f"SSD     {info['disk_percent']:>5.1f} %  ({info['disk_free_gb']:.0f} Go)",
                  fill="white",
                  font=self.font)

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
        draw.text((10, y),
                  f"Load   {la[0]:.2f} {la[1]:.2f} {la[2]:.2f}",
                  fill="lightblue",
                  font=self.font)

        draw.line((10, 242, WIDTH-10, 242), fill="gray")

    def _services(self, draw, info):
        y = 252

        for service, running in info["services"].items():
            name = service.capitalize()
            draw.text((10, y), f"{name:<13}", fill="white", font=self.font)
            color = "lime" if running else "red"
            draw.ellipse((170, y+2, 178, y+10), fill=color)
            y += 18


if __name__ == "__main__":
    from systeminfo import get_system_info

    ui = DashboardDisplay()
    img = ui.render(get_system_info())
    img.save("dashboard_preview.png")
    print("dashboard_preview.png généré.")
