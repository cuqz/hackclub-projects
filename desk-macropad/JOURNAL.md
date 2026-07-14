# Journal - Desk Macropad

## Day 1

Wanted something for the Thing On Desk program. Thought about what would actually look cool sitting on my desk. Came up with a macropad that shows my GitHub commit graph on a little e-ink screen. Whenever someone walks by they can see if I've been coding lately.

Decided on a 4x4 layout. 16 keys is enough for shortcuts, macros, media controls, whatever. The e-ink goes above the keys.

## Day 2 - CAD

Modeled the case in build123d. 110x95x22mm, two halves that screw together with M3 bolts.

Key layout was straightforward, 4x4 grid with 14mm keys and 3mm gaps. The e-ink display window is 59x30mm which is the active area of a Waveshare 2.13 panel.

Put 4 screw bosses in the corners. Wanted 6 but with the e-ink and keys there wasn't room in the middle.

## Day 3 - Firmware

Wrote the Micropython code for the Pico W. It connects to wifi, fetches the GitHub contributions SVG from github.com/users/cuqz/contributions, parses the rect elements to figure out which days have commits, and draws them on the e-ink.

The e-ink part was new to me. They're slow to refresh (a couple seconds) but once they draw they hold the image forever with no power. Perfect for a desk piece - it updates once an hour and shows stats the rest of the time.

Got the waveshare driver downloaded from their github repo. It handles all the SPI stuff, I just call epd.text() and epd.fill_rect().

## What I'd change

- The firmware needs a real API approach instead of scraping the SVG. It works but it's fragile
- Should add error handling for when wifi is down
- 2.13 e-ink is small - might upgrade to 2.9 in a future version
- The Pico W goes to sleep between updates but there's no wake button yet
