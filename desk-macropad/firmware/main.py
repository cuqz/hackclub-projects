# desk macropad firmware
# shows your github commit graph on a waveshare 2.13 e-ink display
# runs on pi pico w
# updates every hour, sleeps between updates

import network
import urequests
import utime
import machine
import ure
import framebuf
import json

# get the real driver from https://github.com/waveshareteam/Pico-ePaper
# copy epd2in13_v3.py into this folder
from epd2in13_v3 import EPD_2in13_V3

# --- config ---
try:
    with open("config.json") as f:
        cfg = json.load(f)
except:
    cfg = {}

WIFI_SSID = cfg.get("wifi_ssid", "your wifi")
WIFI_PASS = cfg.get("wifi_pass", "your password")
GITHUB_USER = cfg.get("github_user", "cuqz")
UPDATE_INTERVAL = cfg.get("update_interval", 3600)  # seconds

LED = machine.Pin("LED", machine.Pin.OUT)

def blink(times=2, delay=0.1):
    for _ in range(times):
        LED.on()
        utime.sleep(delay)
        LED.off()
        utime.sleep(delay)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return True
    wlan.connect(WIFI_SSID, WIFI_PASS)
    timeout = 30
    while not wlan.isconnected() and timeout > 0:
        utime.sleep(1)
        timeout -= 1
    return wlan.isconnected()

def fetch_contributions(username):
    url = "https://github.com/users/" + username + "/contributions"
    for attempt in range(3):
        try:
            resp = urequests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.text
                resp.close()
                return data
            resp.close()
        except:
            pass
        utime.sleep(2)
    return None

def get_shade(fill):
    if not fill or len(fill) < 6:
        return 0
    r = int(fill[0:2], 16)
    g = int(fill[2:4], 16)
    b = int(fill[4:6], 16)
    avg = (r + g + b) / 3
    if avg < 30:
        return 1
    elif avg < 100:
        return 1
    elif avg < 180:
        return 1
    return 0

def draw_graph(epd, svg_data):
    w = epd.width
    h = epd.height
    buf = bytearray(w * h // 8)
    img = framebuf.FrameBuffer(buf, w, h, framebuf.MONO_HLSB)

    img.fill(0)
    img.text("github.com/" + GITHUB_USER, 5, 5, 1)

    squares = ure.findall(r'<rect[^>]*fill="#([0-9a-f]{6})"[^>]*/>', svg_data)

    x = 5
    y = 25
    col = 0
    for fill in squares:
        if get_shade(fill):
            img.fill_rect(x, y, 9, 9, 1)
        x += 13
        col += 1
        if col >= 53:
            col = 0
            x = 5
            y += 13

    img.text("less", 5, y + 15, 1)
    img.text("more", 105, y + 15, 1)

    epd.display(buf)
    epd.sleep()

def show_message(epd, lines):
    w = epd.width
    h = epd.height
    buf = bytearray(w * h // 8)
    img = framebuf.FrameBuffer(buf, w, h, framebuf.MONO_HLSB)
    img.fill(0)
    y = 30
    for line in lines:
        img.text(line, 5, y, 1)
        y += 20
    epd.display(buf)

def main():
    blink(2)
    epd = EPD_2in13_V3()
    epd.init(0)

    show_message(epd, ["desk macropad", "connecting..."])

    if not connect_wifi():
        show_message(epd, ["no wifi connection", "check config.json"])
        epd.sleep()
        return

    svg = fetch_contributions(GITHUB_USER)
    if svg:
        draw_graph(epd, svg)
        blink(1)
    else:
        show_message(epd, ["github api error", "will retry later"])
        epd.sleep()

    # update every hour
    while True:
        utime.sleep(UPDATE_INTERVAL)
        epd.init(0)
        if connect_wifi():
            svg = fetch_contributions(GITHUB_USER)
            if svg:
                draw_graph(epd, svg)
                blink(1)

main()
