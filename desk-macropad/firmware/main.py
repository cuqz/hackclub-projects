# desk macropad firmware
# shows your github commit graph on a waveshare 2.13 e-ink display
# runs on pi pico w

import network
import urequests
import utime
import machine
import ure
import framebuf

# get the real driver from https://github.com/waveshareteam/Pico-ePaper
# copy epd2in13_v3.py into this folder
from epd2in13_v3 import EPD_2in13_V3

# settings
WIFI_SSID = "your wifi"
WIFI_PASS = "your password"
GITHUB_USER = "cuqz"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASS)
        timeout = 30
        while not wlan.isconnected() and timeout > 0:
            utime.sleep(1)
            timeout -= 1
    return wlan.isconnected()

def fetch_contributions(username):
    url = "https://github.com/users/" + username + "/contributions"
    try:
        resp = urequests.get(url)
        if resp.status_code == 200:
            return resp.text
    except:
        pass
    return None

def get_shade(fill):
    if not fill or len(fill) < 6:
        return 0
    r = int(fill[0:2], 16)
    g = int(fill[2:4], 16)
    b = int(fill[4:6], 16)
    avg = (r + g + b) / 3
    if avg < 30:
        return 1  # black
    elif avg < 100:
        return 1  # dark
    elif avg < 180:
        return 1  # light
    return 0  # white

def draw_graph(epd, svg_data):
    w = epd.width
    h = epd.height
    buf = bytearray(w * h // 8)
    img = framebuf.FrameBuffer(buf, w, h, framebuf.MONO_HLSB)
    
    img.fill(0)
    img.text("github.com/" + GITHUB_USER, 5, 5, 1)
    
    # parse the contribution squares from the svg
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

def main():
    epd = EPD_2in13_V3()
    epd.init(0)
    
    # startup screen
    w = epd.width
    h = epd.height
    buf = bytearray(w * h // 8)
    img = framebuf.FrameBuffer(buf, w, h, framebuf.MONO_HLSB)
    img.fill(0)
    img.text("desk macropad", 5, 30, 1)
    img.text("connecting...", 5, 50, 1)
    epd.display(buf)
    
    if connect_wifi():
        svg = fetch_contributions(GITHUB_USER)
        if svg:
            draw_graph(epd, svg)
        else:
            img.fill(0)
            img.text("api error", 5, 70, 1)
            epd.display(buf)
            epd.sleep()
    else:
        img.fill(0)
        img.text("no wifi", 5, 70, 1)
        epd.display(buf)
        epd.sleep()

main()
