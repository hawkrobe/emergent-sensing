
GAME_LENGTH = 1.0 # minutes

SIDE_WIDTH = 25

DISCRETE_BG_RADIUS = 50

STOP_AND_CLICK = True

WORLD = {"width" : 485, "height" : 280}
SIZE= { "x":5, "y":5, "hx":2.5, "hy":2.5 }
POS_LIMITS = {
    "x_min": SIZE["hx"],
    "x_max": WORLD["width"] - SIZE["hx"],
    "y_min": SIZE["hy"],
    "y_max": WORLD["height"] - SIZE["hy"]
}

SPOT_START_PROB = 1.0 / (10*8)
SPOT_SHIFT_PROB = 1.0 / (10*8)

LOW_SCORE = 0.2
