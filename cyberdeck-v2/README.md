# Cyberdeck v2

Handheld terminal I've been working on. Raspberry Pi Pico inside, 2.8" screen, 20 mechanical switches, 18650 battery.

## Files

- `cad/cyberdeck.py` - the case model, opens in build123d
- `cad/cyberdeck.step` - step file for editing
- `cad/cyberdeck.stl` - stl for printing

## Case specs

180mm x 90mm x 24mm. Two halves that screw together with M3 bolts. 2mm walls. PLA or PETG, 0.2mm layers.

## Parts list

Roughly $40 in parts:
- Pi Pico (or Pico W) - $4
- 2.8" TFT SPI display - $8
- 20x MX switches - $8
- 20x 1N4148 diodes - $1
- 18650 battery - $5
- TP4056 charger - $1
- USB-C breakout - $2
- 6x M3x10 screws - $1
- PLA filament ~90g - $6

## Build notes

Print the bottom shell with the cavity facing up, needs supports for the screw bosses. Faceplate can print flat. Sand the switch holes if they're tight, 0.3mm clearance is usually enough for FDM.

See JOURNAL.md for the full build log.
