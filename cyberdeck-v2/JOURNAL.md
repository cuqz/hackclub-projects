# Build Journal — Cyberdeck v2

## Day 1

Wanted a handheld terminal thing I could carry around. Not a laptop or a phone, just something chunky that looks like it belongs in a sci-fi movie. Decided to make a two-piece case this time since my last one was a single shell that was annoying to assemble.

Pi Pico because it's $4 and I have a few. 2.8" TFT screen. 5x4 ortho keypad for thumb typing.

## Day 2

Modeled the case in build123d. Went through three versions:

1. 160x80mm - too cramped for screen + keyboard
2. 180x90mm - this works, everything fits with room for screw bosses
3. Added battery trough on one side so the 18650 doesn't float around inside

Screw bosses were the hardest part. Had to make sure they don't intersect the battery or the Pi Pico. Put three on each long edge.

Keyboard area took some measuring. MX switches are 14mm apart center-to-center. With 2.5mm gaps the whole 5x4 block is about 82x66mm.

Screen went above the keyboard with a 65x45mm window.

## Day 3

Exported the STEP and STL. Bottom shell has:
- Internal cavity 10mm deep
- Pi Pico pocket
- 18650 trough
- USB-C notch
- 6 M3 screw bosses

Top faceplate has:
- Screen window
- 20 switch cutouts
- Screw clearance holes

Printed a quick test of the bottom shell. USB-C notch lines up. Screw bosses need a tiny bit of filing.

## Stuff I'd change

- Make screw bosses 1mm taller for more thread
- Could probably drop wall thickness to 1.6mm to save weight
- Add a lip around the screen window so the display has somewhere to sit
