import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Rectangle, Polygon, Arc
from IPython.display import display
import random as rd

_fig = None
_ax = None

width = 0
height = 0

_stroke = (0, 0, 0)
_fill = None
_strokeWeight = 1
_textSize = 12


# ============================================================
# COULEURS
# ============================================================

BLACK = "#000000"
WHITE = "#FFFFFF"
RED = "#FF0000"
GREEN = "#00FF00"
BLUE = "#0000FF"
YELLOW = "#FFFF00"
CYAN = "#00FFFF"
MAGENTA = "#FF00FF"


# ============================================================
# CONVERSION DES COULEURS
# ============================================================

def _color(c):

    if isinstance(c, str):

        c = c.strip().lstrip("#")

        if len(c) == 6:
            return tuple(
                int(c[i:i+2], 16) / 255
                for i in (0, 2, 4)
            )

        if len(c) == 3:
            return tuple(
                int(c[i] * 2, 16) / 255
                for i in range(3)
            )

        raise ValueError("Couleur hexadécimale invalide")

    if isinstance(c, (tuple, list)):

        if len(c) != 3:
            raise ValueError(
                "Une couleur RGB doit contenir 3 valeurs"
            )

        return tuple(x / 255 for x in c)

    if isinstance(c, (int, float)):

        v = c / 255

        return (v, v, v)

    raise ValueError("Couleur inconnue")


# ============================================================
# SIZE
# ============================================================

def size(w, h):

    global _fig, _ax
    global width, height

    width = w
    height = h

    plt.close("all")

    _fig, _ax = plt.subplots(
        figsize=(8, 8)
    )

    _ax.set_xlim(0, width)
    _ax.set_ylim(height, 0)

    _ax.set_aspect("equal")

    _ax.axis("off")

    _ax.set_facecolor("white")
    _fig.patch.set_facecolor("white")

    display(_fig)


# ============================================================
# BACKGROUND
# ============================================================

def background(c):

    color = _color(c)

    _ax.set_facecolor(color)
    _fig.patch.set_facecolor(color)

    _fig.canvas.draw()


# ============================================================
# STROKE
# ============================================================

def stroke(c):

    global _stroke

    _stroke = _color(c)


def noStroke():

    global _stroke

    _stroke = None


# ============================================================
# FILL
# ============================================================

def fill(c):

    global _fill

    _fill = _color(c)


def noFill():

    global _fill

    _fill = None


# ============================================================
# STROKE WEIGHT
# ============================================================

def strokeWeight(n):

    global _strokeWeight

    _strokeWeight = n


# ============================================================
# POINT
# ============================================================

def point(x, y):

    if _stroke is None:
        return

    _ax.plot(
        x,
        y,
        marker="o",
        markersize=max(1, _strokeWeight * 2),
        color=_stroke,
        markeredgewidth=0
    )


# ============================================================
# LINE
# ============================================================

def line(x1, y1, x2, y2):

    if _stroke is None:
        return

    _ax.plot(
        [x1, x2],
        [y1, y2],
        color=_stroke,
        linewidth=_strokeWeight
    )


# ============================================================
# CIRCLE
# ============================================================

def circle(x, y, d):

    edge = _stroke if _stroke is not None else "none"
    face = _fill if _fill is not None else "none"

    c = Circle(
        (x, y),
        d / 2,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight
    )

    _ax.add_patch(c)


# ============================================================
# ELLIPSE
# ============================================================

def ellipse(x, y, w, h):

    edge = _stroke if _stroke is not None else "none"
    face = _fill if _fill is not None else "none"

    e = Ellipse(
        (x, y),
        w,
        h,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight
    )

    _ax.add_patch(e)


# ============================================================
# RECT
# ============================================================

def rect(x, y, w, h):

    edge = _stroke if _stroke is not None else "none"
    face = _fill if _fill is not None else "none"

    r = Rectangle(
        (x, y),
        w,
        h,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight
    )

    _ax.add_patch(r)


# ============================================================
# SQUARE
# ============================================================

def square(x, y, s):

    rect(x, y, s, s)


# ============================================================
# TRIANGLE
# ============================================================

def triangle(x1, y1, x2, y2, x3, y3):

    edge = _stroke if _stroke is not None else "none"
    face = _fill if _fill is not None else "none"

    t = Polygon(
        [
            (x1, y1),
            (x2, y2),
            (x3, y3)
        ],
        closed=True,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight
    )

    _ax.add_patch(t)


# ============================================================
# ARC
# ============================================================

def arc(x, y, w, h, start, stop):

    if _stroke is None:
        return

    a = Arc(
        (x, y),
        w,
        h,
        theta1=start,
        theta2=stop,
        color=_stroke,
        linewidth=_strokeWeight
    )

    _ax.add_patch(a)


# ============================================================
# TEXT
# ============================================================

def textSize(n):

    global _textSize

    _textSize = n


def text(s, x, y):

    color = _stroke if _stroke is not None else (0, 0, 0)

    _ax.text(
        x,
        y,
        str(s),
        fontsize=_textSize,
        color=color
    )


# ============================================================
# RANDOM
# ============================================================

def random(a, b=None):

    if b is None:
        return rd.uniform(0, a)

    return rd.uniform(a, b)


# ============================================================
# RANDOM SEED
# ============================================================

def randomSeed(seed):

    rd.seed(seed)


# ============================================================
# SAVE
# ============================================================

def save(filename):

    if _fig is None:
        return

    _fig.savefig(
        filename,
        bbox_inches="tight"
    )
