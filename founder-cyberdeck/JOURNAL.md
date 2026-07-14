# JOURNAL.md — Founder Cyberdeck

## Day 1 — Figuring out what to build

I wanted to make something for Outpost that wasn't just another macropad. Everyone makes macropads. I've been into cyberdecks for a while — those portable terminal things you see on r/cyberdeck. They look like props from a movie but people actually build them.

I also really like Attack on Titan. So I thought: what if I mash the two together? A handheld terminal that looks like it belongs in the AoT universe. Not a laptop, not a phone, just this weird little box with a screen and keyboard.

**What I want it to do:**
- Be handheld, roughly the size of a Nintendo DS
- Have a real screen, not just OLEDs
- Mechanical keyboard because clicky switches are fun
- Battery powered so I can actually use it places
- Run on something cheap like a Pico

**Parts I know I need:**
- 3.5" TFT screen
- Raspberry Pi Pico W ($6, can't beat that)
- 15 Cherry MX switches I have lying around
- 2 rotary encoders for scrolling
- A joystick for navigation
- 18650 batteries (I have a few from old vape pens)
- USB-C for charging

---

## Day 2 — Actually designing the thing

Started modeling the case. Went through a few versions before getting something usable.

**The dimensions I settled on:**
180mm wide, 100mm tall, 30mm thick closed. That's about the size of a 3DS XL.

**First attempt — total fail:**
- USB cutout was too narrow by 0.5mm
- The switch holes were perfect circles — Cherry MX switches have these little alignment pegs that need notches
- Made the battery compartment as solid cylinders instead of hollow tubes with vents
- The screen angle created an overhang that would need a ton of support material

**Second attempt — way better:**
Fixed the measurements. Added alignment notches for the switches, vent slots for the batteries, chamfered the USB hole. The second STL is actually usable. The back panel has this organic ribbed texture that looks exactly like Titan spinal columns. That part came out sick.

**What the STL has:**
- The full case body with 2.4mm walls
- A recess for the 3.5" screen angled at 30 degrees
- 15 holes for Cherry MX switches in a 5x3 grid
- 2 holes for rotary encoders on either side of the top row
- A hole for the joystick on the left edge
- A cutout for a small OLED status screen above the keyboard
- USB-C port cutout on the bottom
- Battery compartment for 2x 18650s with ventilation slots
- Screw bosses for M3 screws at 6 points
- 4 mounting posts for the Pico W
- Ribbed texture on the back

The file is about 1.4MB. Probably needs cleanup in the slicer.

---

## Day 3 — What went wrong and what I learned

**Things that surprised me:**
1. You have to be really precise with measurements or things don't line up
2. Organic textures are actually easier to model than straight precise lines
3. Every single cutout needs to be verified manually — a switch hole that's slightly off means the whole part is scrap
4. Splitting the case into front and back halves is more work than I expected

**Stuff I'd do different:**
- I should have started with a cardboard mockup to check ergonomics before modeling anything
- The 30 degree screen angle might be too aggressive — might flatten it to 20 in v2
- Need to add tolerance gaps for the snap-fit between case halves

**Next up:**
- [ ] Split the STL into front half, back half, and battery door
- [ ] Slice it in Bambu Studio with tree supports
- [ ] Print a test in PLA to check fitment
- [ ] Order the actual electronics
- [ ] Wire everything up once the case fits

---

## Parts cost

Rough breakdown:
- 3.5" TFT screen - $15
- Pi Pico W - $6
- 15x Cherry MX switches - $12 (already have some)
- Keycaps - $10
- 2x EC11 encoders - $4
- Joystick module - $3
- Small OLED - $5
- 2x 18650 batteries - $14
- BMS board - $4
- USB-C breakout - $2
- M3 hardware - $5
- PLA filament - $10

Comes out to about $90. Could add RGB underglow if I'm feeling fancy but that's extra.

---

*Started July 11, 2026*
*Built for Hack Club Outpost*
