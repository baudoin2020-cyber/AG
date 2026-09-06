# -*- coding: utf-8 -*-

AG_VERSION = "2026-09-06-01"

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Circle, Ellipse, Rectangle, Polygon, Arc
import random as rd

try:
    from IPython import get_ipython
    from IPython.display import display, clear_output
except Exception:
    get_ipython = None
    display = None
    clear_output = None


_fig = None
_ax = None
_canvas = None

width = 0
height = 0

_stroke = (0, 0, 0)
_fill = None
_strokeWeight = 1
_textSize = 12
_zorder = 1

_dirty = False
_hook_registered = False


BLACK = "#000000"
WHITE = "#FFFFFF"
RED = "#FF0000"
GREEN = "#00FF00"
BLUE = "#0000FF"
YELLOW = "#FFFF00"
CYAN = "#00FFFF"
MAGENTA = "#FF00FF"


def _color(c):

    if isinstance(c, str):

        c = c.strip().lstrip("#")

        if len(c) == 6:
            return tuple(
                int(c[i:i+2], 16) / 255.0
                for i in (0, 2, 4)
            )

        if len(c) == 3:
            return tuple(
                int(c[i] * 2, 16) / 255.0
                for i in range(3)
            )

        raise ValueError("Couleur hexadecimale invalide")

    if isinstance(c, (tuple, list)):

        if len(c) != 3:
            raise ValueError("Une couleur RGB doit contenir 3 valeurs")

        if max(c) <= 1:
            return tuple(c)

        return tuple(x / 255.0 for x in c)

    if isinstance(c, (int, float)):

        v = c / 255.0
        return (v, v, v)

    raise ValueError("Couleur inconnue")


def _next_zorder():

    global _zorder

    z = _zorder
    _zorder += 1

    return z


def _mark_dirty():

    global _dirty

    _dirty = True


def _display_once(*args, **kwargs):

    global _dirty

    if not _dirty:
        return

    if _fig is None:
        return

    if display is None:
        return

    try:
        if _canvas is not None:
            _canvas.draw()
    except Exception:
        pass

    try:
        display(_fig)
    except Exception:
        pass

    _dirty = False


def _register_hook():

    global _hook_registered

    if _hook_registered:
        return

    if get_ipython is None:
        return

    try:
        ip = get_ipython()

        if ip is not None and hasattr(ip, "events"):
            ip.events.register(
                "post_run_cell",
                _display_once
            )

            _hook_registered = True

    except Exception:
        pass


_register_hook()


def size(w, h):

    global _fig, _ax, _canvas
    global width, height
    global _zorder

    width = w
    height = h
    _zorder = 1

    dpi = 100.0

    _fig = Figure(
        figsize=(
            float(w) / dpi,
            float(h) / dpi
        ),
        dpi=dpi
    )

    _canvas = FigureCanvasAgg(_fig)

    _ax = _fig.add_axes(
        [0, 0, 1, 1]
    )

    _ax.set_xlim(0, width)
    _ax.set_ylim(height, 0)

    _ax.set_aspect("equal")
    _ax.axis("off")

    _ax.patch.set_facecolor("white")
    _fig.patch.set_facecolor("white")

    _mark_dirty()


def background(c):

    color = _color(c)

    _ax.patch.set_facecolor(color)
    _fig.patch.set_facecolor(color)

    _mark_dirty()


def stroke(c):

    global _stroke

    _stroke = _color(c)


def noStroke():

    global _stroke

    _stroke = None


def fill(c):

    global _fill

    _fill = _color(c)


def noFill():

    global _fill

    _fill = None


def strokeWeight(n):

    global _strokeWeight

    _strokeWeight = n


def point(x, y):

    if _stroke is None:
        return

    _ax.plot(
        x,
        y,
        marker="o",
        markersize=max(1, _strokeWeight * 2),
        color=_stroke,
        markeredgewidth=0,
        zorder=_next_zorder()
    )

    _mark_dirty()


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

    _mark_dirty()


def circle(x, y, d):

    edge = _stroke if _stroke is not None else "none"
    face = _fill if _fill is not None else "none"

    shape = Circle(
        (x, y),
        d / 2.0,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight,
        zorder=_next_zorder()
    )

    _ax.add_patch(shape)

    _mark_dirty()


def ellipse(x, y, w, h):

    edge = _stroke if _stroke is not None else "none"
    face = _fill if _fill is not None else "none"

    shape = Ellipse(
        (x, y),
        w,
        h,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight,
        zorder=_next_zorder()
    )

    _ax.add_patch(shape)

    _mark_dirty()


def rect(x, y, w, h):

    edge = _stroke if _stroke is not None else "none"
    face = _fill if _fill is not None else "none"

    shape = Rectangle(
        (x, y),
        w,
        h,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight,
        zorder=_next_zorder()
    )

    _ax.add_patch(shape)

    _mark_dirty()


def square(x, y, s):

    rect(x, y, s, s)


def triangle(
    x1, y1,
    x2, y2,
    x3, y3
):

    edge = _stroke if _stroke is not None else "none"
    face = _fill if _fill is not None else "none"

    shape = Polygon(
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

    _ax.add_patch(shape)

    _mark_dirty()


def arc(
    x, y,
    w, h,
    start, stop
):

    if _stroke is None:
        return

    shape = Arc(
        (x, y),
        w,
        h,
        theta1=start,
        theta2=stop,
        color=_stroke,
        linewidth=_strokeWeight,
        zorder=_next_zorder()
    )

    _ax.add_patch(shape)

    _mark_dirty()


def textSize(n):

    global _textSize

    _textSize = n


def text(s, x, y):

    color = _fill if _fill is not None else _stroke

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

    _mark_dirty()


def random(a, b=None):

    if b is None:
        return rd.uniform(0, a)

    return rd.uniform(a, b)


def randomSeed(seed):

    rd.seed(seed)


def clear():

    global _zorder

    _ax.cla()

    _ax.set_xlim(0, width)
    _ax.set_ylim(height, 0)

    _ax.set_aspect("equal")
    _ax.axis("off")

    _ax.patch.set_facecolor("white")
    _fig.patch.set_facecolor("white")

    _zorder = 1

    _mark_dirty()


def save(filename):

    if _fig is None:
        return

    if _canvas is not None:
        try:
            _canvas.draw()
        except Exception:
            pass

    _fig.savefig(
        filename,
        dpi=_fig.dpi
    )
