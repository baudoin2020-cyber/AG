```python
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Rectangle, Polygon, Arc
from IPython.display import display
import random as rd


# ============================================================
# VARIABLES GLOBALES
# ============================================================

_fig = None
_ax = None

width = 0
height = 0

_stroke = (0, 0, 0)
_fill = None
_strokeWeight = 1
_textSize = 12

_zorder = 1


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

    # Couleur hexadécimale
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

        raise ValueError(
            "Couleur hexadécimale invalide"
        )

    # Couleur RGB
    if isinstance(c, (tuple, list)):

        if len(c) != 3:

            raise ValueError(
                "Une couleur RGB doit contenir 3 valeurs"
            )

        # valeurs déjà entre 0 et 1
        if max(c) <= 1:

            return tuple(c)

        # valeurs entre 0 et 255
        return tuple(
            x / 255
            for x in c
        )

    # Niveau de gris
    if isinstance(c, (int, float)):

        v = c / 255

        return (v, v, v)

    raise ValueError("Couleur inconnue")


# ============================================================
# ORDRE DE DESSIN
# ============================================================

def _next_zorder():

    global _zorder

    z = _zorder

    _zorder += 1

    return z


# ============================================================
# SIZE
# ============================================================

def size(w, h):

    global _fig, _ax
    global width, height
    global _zorder

    width = w
    height = h

    _zorder = 1

    plt.close("all")

    # Respect du rapport largeur / hauteur
    ratio = w / h

    if ratio >= 1:

        figsize = (8, 8 / ratio)

    else:

        figsize = (8 * ratio, 8)

    _fig, _ax = plt.subplots(
        figsize=figsize
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
        markersize=max(
            1,
            _strokeWeight * 2
        ),
        color=_stroke,
        markeredgewidth=0,
        zorder=_next_zorder()
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
        linewidth=_strokeWeight,
        zorder=_next_zorder()
    )


# ============================================================
# CIRCLE
# Processing :
# circle(x, y, diameter)
# ============================================================

def circle(x, y, d):

    edge = (
        _stroke
        if _stroke is not None
        else "none"
    )

    face = (
        _fill
        if _fill is not None
        else "none"
    )

    c = Circle(
        (x, y),
        d / 2,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight,
        zorder=_next_zorder()
    )

    _ax.add_patch(c)


# ============================================================
# ELLIPSE
# Processing :
# ellipse(x, y, width, height)
# ============================================================

def ellipse(x, y, w, h):

    edge = (
        _stroke
        if _stroke is not None
        else "none"
    )

    face = (
        _fill
        if _fill is not None
        else "none"
    )

    e = Ellipse(
        (x, y),
        w,
        h,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight,
        zorder=_next_zorder()
    )

    _ax.add_patch(e)


# ============================================================
# RECT
# Processing :
# rect(x, y, width, height)
# ============================================================

def rect(x, y, w, h):

    edge = (
        _stroke
        if _stroke is not None
        else "none"
    )

    face = (
        _fill
        if _fill is not None
        else "none"
    )

    r = Rectangle(
        (x, y),
        w,
        h,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight,
        zorder=_next_zorder()
    )

    _ax.add_patch(r)


# ============================================================
# SQUARE
# ============================================================

def square(x, y, s):

    rect(
        x,
        y,
        s,
        s
    )


# ============================================================
# TRIANGLE
# ============================================================

def triangle(
    x1, y1,
    x2, y2,
    x3, y3
):

    edge = (
        _stroke
        if _stroke is not None
        else "none"
    )

    face = (
        _fill
        if _fill is not None
        else "none"
    )

    t = Polygon(
        [
            (x1, y1),
            (x2, y2),
            (x3, y3)
        ],
        closed=True,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight,
        zorder=_next_zorder()
    )

    _ax.add_patch(t)


# ============================================================
# ARC
# ============================================================

def arc(
    x, y,
    w, h,
    start, stop
):

    if _stroke is None:

        return

    a = Arc(
        (x, y),
        w,
        h,
        theta1=start,
        theta2=stop,
        color=_stroke,
        linewidth=_strokeWeight,
        zorder=_next_zorder()
    )

    _ax.add_patch(a)


# ============================================================
# TEXT SIZE
# ============================================================

def textSize(n):

    global _textSize

    _textSize = n


# ============================================================
# TEXT
# ============================================================

def text(s, x, y):

    color = (
        _fill
        if _fill is not None
        else _stroke
    )

    if color is None:

        color = (0, 0, 0)

    _ax.text(
        x,
        y,
        str(s),
        fontsize=_textSize,
        color=color,
        zorder=_next_zorder()
    )


# ============================================================
# RANDOM
# Processing :
# random(high)
# random(low, high)
# ============================================================

def random(a, b=None):

    if b is None:

        return rd.uniform(
            0,
            a
        )

    return rd.uniform(
        a,
        b
    )


# ============================================================
# RANDOM SEED
# ============================================================

def randomSeed(seed):

    rd.seed(seed)


# ============================================================
# CLEAR
# ============================================================

def clear():

    global _zorder

    _ax.cla()

    _ax.set_xlim(
        0,
        width
    )

    _ax.set_ylim(
        height,
        0
    )

    _ax.set_aspect("equal")

    _ax.axis("off")

    _zorder = 1


# ============================================================
# SAVE
# ============================================================

def save(filename):

    if _fig is None:

        return

    _fig.savefig(
        filename,
        bbox_inches="tight",
        pad_inches=0
    )
```
