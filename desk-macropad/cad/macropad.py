# desk macropad - 4x4 keys + e-ink display showing github commit graph
# two-piece case: top plate + bottom shell

from build123d import *
from cadpy.assembly import label_shape

# case size
W = 110.0
D = 95.0
H = 22.0
WALL = 2.0
FILLET_R = 5.0

# 4x4 keys
K = 14.0
KG = 3.0
KC = 4
KR = 4
GRID_W = (KC - 1) * (K + KG)
GRID_D = (KR - 1) * (K + KG)
KEYS_X = 0.0
KEYS_Y = -12.0

# e-ink display (waveshare 2.13)
EI_W = 59.0
EI_D = 30.0
EI_X = 0.0
EI_Y = 25.0

# screw bosses
BOSS_OD = 6.0
BOSS_ID = 3.4
BOSS_POS = [
    (-42, -35), (42, -35),
    (-42,  35), (42,  35),
]


def make_bottom():
    with BuildPart() as p:
        with BuildSketch():
            RectangleRounded(W, D, FILLET_R)
        extrude(amount=H / 2)

        # round top edge
        top = p.faces().sort_by(Axis.Z)[-1].edges()
        fillet(top, radius=1.0)

        # hollow
        with BuildSketch(Plane.XY.offset(WALL)):
            RectangleRounded(W - 2*WALL, D - 2*WALL, FILLET_R - 0.5)
        extrude(amount=H / 2 - WALL, mode=Mode.SUBTRACT)

        # screw posts
        for bx, by in BOSS_POS:
            with Locations((bx, by)):
                Cylinder(radius=BOSS_OD / 2, height=H / 2 - WALL)
                with Locations((0, 0, H / 2 - WALL - 1)):
                    Hole(radius=BOSS_ID / 2, depth=H / 2 - WALL)

    return p.part


def make_top():
    with BuildPart() as p:
        with BuildSketch():
            RectangleRounded(W, D, FILLET_R)
        extrude(amount=H / 2)

        # round top
        top = p.faces().sort_by(Axis.Z)[-1].edges()
        fillet(top, radius=1.5)

        # e-ink window
        with Locations((EI_X, EI_Y)):
            with BuildSketch():
                RectangleRounded(EI_W, EI_D, 3)
            extrude(amount=H / 2, mode=Mode.SUBTRACT)

        # shallow recess around e-ink
        with Locations((EI_X, EI_Y)):
            with BuildSketch():
                RectangleRounded(EI_W + 4, EI_D + 4, 3)
            extrude(amount=1.5, mode=Mode.SUBTRACT)

        # 16 switch holes
        grid_w = (KC - 1) * (K + KG)
        grid_d = (KR - 1) * (K + KG)
        for row in range(KR):
            for col in range(KC):
                kx = KEYS_X - grid_w / 2 + col * (K + KG)
                ky = KEYS_Y - grid_d / 2 + row * (K + KG)
                with Locations((kx, ky)):
                    with BuildSketch():
                        RectangleRounded(K + 0.3, K + 0.3, 1)
                    extrude(amount=H / 2, mode=Mode.SUBTRACT)

        # screw holes
        for bx, by in BOSS_POS:
            with Locations((bx, by)):
                with BuildSketch():
                    Circle(radius=BOSS_ID / 2)
                extrude(amount=H / 2, mode=Mode.SUBTRACT)

    return p.part


def gen_step():
    bottom = make_bottom()
    top_plate = make_top()

    bottom = label_shape(bottom, "bottom_shell")
    top_moved = label_shape(Pos(Z=H / 2) * top_plate, "top_faceplate")

    return Compound(label="desk_macropad", children=[bottom, top_moved])
