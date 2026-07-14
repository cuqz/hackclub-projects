# Desk Macropad

A 16-key macropad with an e-ink display on top that shows my GitHub commit graph. Sits on my desk at all times.

## What it does

- 4x4 mechanical keys you can program for anything
- 2.13 e-ink display that fetches and shows your GitHub contribution graph
- Updates every hour over wifi
- Pi Pico W inside

## Files

- `cad/macropad.py` - 3d printed case (top + bottom halves)
- `cad/macropad.step` - step file for editing
- `cad/macropad.stl` - stl for printing
- `firmware/main.py` - micropython code for the pico w
- `firmware/waveshare_epd.py` - driver notes (download from waveshare)

## Parts

- Raspberry Pi Pico W - $6
- 16x MX-compatible switches - $8
- 16x keycaps - $5
- Waveshare 2.13 e-ink display - $12
- 4x M3x10 screws - $1
- PLA filament - $5

About $37 total.

## How to build

1. Print the case (PLA, 0.2mm, needs supports for screw bosses)
2. Wire the switches in a 4x4 matrix to the Pico
3. Connect the e-ink display via SPI
4. Flash main.py to the Pico
5. Set your wifi and github username in main.py
6. Screw it together and put it on your desk
