# cyberdeck v2 case
# 180x90x24mm two-piece enclosure for pi pico terminal
# bottom shell + top faceplate

from build123d import *
from cadpy.assembly import label_shape

# -- dimensions --
WIDTH = 180.0
DEPTH = 90.0
TOTAL_H = 24.0
HALF_H = TOTAL_H / 2
WALL = 2.0
FILLET_R = 6.0

# pi pico
PICO_W = 51.0
PICO_D = 21.0
PICO_H = 1.5

# 2.8 tft screen
SCREEN_W = 65.0
SCREEN_D = 45.0
SCR_Y = 8.0

# keyboard - 5x4 ortho
KEY = 14.0
KGAP = 2.5
KCOLS = 5
KROWS = 4
KBLOCK_W = KCOLS * KEY + (KCOLS - 1) * KGAP + 4
KBLOCK_D = KROWS * KEY + (KROWS - 1) * KGAP + 4
KB_Y = -18.0

# 18650 battery
BATT_R = 9.0
BATT_L = 65.0
BATT_Y = 32.0

# usb-c
USBC_W = 10.0
USBC_H = 4.5

# m3 screw bosses, 6 of em
BOSS_OD = 6.0
BOSS_ID = 3.4
BOSS_POS = [
    (-75, -35), (75, -35),
    (-75,  35), (75,  35),
    (-75,   0), (75,   0),
]


def make_bottom():
    with BuildPart() as p:
        with BuildSketch():
            RectangleRounded(WIDTH, DEPTH, FILLET_R)
        extrude(amount=HALF_H)

        # round the top edges before cutting anything
        top_perim = p.faces().sort_by(Axis.Z)[-1].edges()
        fillet(top_perim, radius=1.0)

        # hollow out the middle
        with BuildSketch(Plane.XY.offset(WALL)):
            RectangleRounded(WIDTH - 2*WALL, DEPTH - 2*WALL, FILLET_R - 1)
        extrude(amount=HALF_H - WALL, mode=Mode.SUBTRACT)

        # pico sits here
        with Locations((0, -22)):
            with BuildSketch(Plane.XY.offset(WALL)):
                RectangleRounded(PICO_W + 1, PICO_D + 1, 1.5)
            extrude(amount=PICO_H + 0.5, mode=Mode.SUBTRACT)

        # battery goes here
        with Locations((0, BATT_Y)):
            with BuildSketch(Plane.XY.offset(WALL)):
                RectangleRounded(BATT_L, BATT_R * 2 + 2, 3)
            extrude(amount=HALF_H - WALL, mode=Mode.SUBTRACT)

        # usb-c cutout on the front edge
        with Locations((0, -DEPTH / 2)):
            with BuildSketch(Plane.XY.offset(HALF_H - WALL - 1)):
                RectangleRounded(USBC_W, USBC_H, 1)
            extrude(amount=WALL + 1, mode=Mode.SUBTRACT)

        # screw posts
        for bx, by in BOSS_POS:
            with Locations((bx, by)):
                Cylinder(radius=BOSS_OD / 2, height=HALF_H - WALL)
                with Locations((0, 0, HALF_H - WALL - 1)):
                    Hole(radius=BOSS_ID / 2, depth=HALF_H - WALL)

    return p.part


def make_top():
    with BuildPart() as p:
        with BuildSketch():
            RectangleRounded(WIDTH, DEPTH, FILLET_R)
        extrude(amount=HALF_H)

        # round the top so it feels nice in hand
        top_perim = p.faces().sort_by(Axis.Z)[-1].edges()
        fillet(top_perim, radius=1.5)

        # screen hole
        with Locations((0, SCR_Y)):
            with BuildSketch():
                RectangleRounded(SCREEN_W, SCREEN_D, 3)
            extrude(amount=HALF_H, mode=Mode.SUBTRACT)

        # keyboard recess + switch holes
        with Locations((0, KB_Y)):
            with BuildSketch():
                RectangleRounded(KBLOCK_W, KBLOCK_D, 2)
            extrude(amount=2.5, mode=Mode.SUBTRACT)

        # 20 individual mx switch holes with a bit of clearance
        grid_w = (KCOLS - 1) * (KEY + KGAP)
        grid_d = (KROWS - 1) * (KEY + KGAP)
        for row in range(KROWS):
            for col in range(KCOLS):
                kx = -grid_w / 2 + col * (KEY + KGAP)
                ky = KB_Y - grid_d / 2 + row * (KEY + KGAP)
                with Locations((kx, ky)):
                    with BuildSketch():
                        RectangleRounded(KEY + 0.3, KEY + 0.3, 1)
                    extrude(amount=HALF_H, mode=Mode.SUBTRACT)

        # screw holes to match the bottom bosses
        for bx, by in BOSS_POS:
            with Locations((bx, by)):
                with BuildSketch():
                    Circle(radius=BOSS_ID / 2)
                extrude(amount=HALF_H, mode=Mode.SUBTRACT)

    return p.part


def gen_step():
    bottom = make_bottom()
    top_plate = make_top()

    bottom = label_shape(bottom, "bottom_shell")
    top_moved = label_shape(Pos(Z=HALF_H) * top_plate, "top_faceplate")

    return Compound(label="cyberdeck_v2", children=[bottom, top_moved])
