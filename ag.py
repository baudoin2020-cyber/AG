import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Rectangle, Polygon, Arc
import random as rd

try:
    from IPython.display import set_matplotlib_close
    set_matplotlib_close(False)
except Exception:
    try:
        ip = get_ipython()
        if ip is not None:
            ip.run_line_magic("config", "InlineBackend.close_figures=False")
    except Exception:
        pass

try:
    plt.ion()
except Exception:
    pass


_fig = None
_ax = None

width = 0
height = 0

_stroke = (0, 0, 0)
_fill = None
_strokeWeight = 1
_textSize = 12
_zorder = 1


BLACK = "#000000"
WHITE = "#FFFFFF"
RED = "#FF0000"
GREEN = "#00FF00"
BLUE = "#0000FF"
YELLOW = "#FFFF00"
CYAN = "#00FFFF"
MAGENTA = "#FF00FF"


def _set_background(ax, color):
    if hasattr(ax, "set_facecolor"):
        ax.set_facecolor(color)
    elif hasattr(ax, "set_axis_bgcolor"):
        ax.set_axis_bgcolor(color)


def _refresh():
    """
    Met à jour la figure sans l'afficher explicitement.
    Jupyter l'affiche automatiquement une seule fois en fin de cellule.
    """
    if _fig is None:
        return

    try:
        _fig.canvas.draw_idle()
    except Exception:
        try:
            _fig.canvas.draw()
        except Exception:
            pass

    try:
        _fig.canvas.flush_events()
    except Exception:
        pass


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


def size(w, h):
    global _fig, _ax
    global width, height
    global _zorder

    width = w
    height = h
    _zorder = 1

    plt.close("all")

    # Processing : size(w, h) correspond à w x h pixels.
    # Matplotlib exprime figsize en pouces : pixels = pouces * dpi.
    dpi = 100.0
    figsize = (float(w) / dpi, float(h) / dpi)

    _fig, _ax = plt.subplots(
        figsize=figsize,
        dpi=dpi
    )

    # La zone de dessin occupe exactement toute la figure,
    # sans marges Matplotlib autour du canevas.
    _fig.subplots_adjust(
        left=0,
        right=1,
        bottom=0,
        top=1
    )

    _ax.set_xlim(0, width)
    _ax.set_ylim(height, 0)
    _ax.set_aspect("equal")
    _ax.axis("off")

    _set_background(_ax, "white")

    if hasattr(_fig.patch, "set_facecolor"):
        _fig.patch.set_facecolor("white")

    _refresh()


def background(c):
    color = _color(c)

    _set_background(_ax, color)

    if hasattr(_fig.patch, "set_facecolor"):
        _fig.patch.set_facecolor(color)

    _refresh()


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

    _refresh()


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

    _refresh()


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
    _refresh()


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
    _refresh()


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
    _refresh()


def square(x, y, s):
    rect(x, y, s, s)


def triangle(x1, y1, x2, y2, x3, y3):
    edge = _stroke if _stroke is not None else "none"
    face = _fill if _fill is not None else "none"

    shape = Polygon(
        [(x1, y1), (x2, y2), (x3, y3)],
        closed=True,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight,
        zorder=_next_zorder()
    )

    _ax.add_patch(shape)
    _refresh()


def arc(x, y, w, h, start, stop):
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
    _refresh()


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

    _refresh()


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

    _set_background(_ax, "white")

    _zorder = 1
    _refresh()


def save(filename):
    if _fig is None:
        return

    # Conserve exactement les dimensions définies par size().
    _fig.savefig(
        filename,
        dpi=_fig.dpi
    )
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Rectangle, Polygon, Arc
import random as rd

try:
    from IPython.display import display
except Exception:
    display = None

try:
    from IPython.display import set_matplotlib_close
    set_matplotlib_close(False)
except Exception:
    try:
        ip = get_ipython()
        if ip is not None:
            ip.run_line_magic("config", "InlineBackend.close_figures=False")
    except Exception:
        pass

try:
    plt.ion()
except Exception:
    pass


_fig = None
_ax = None

width = 0
height = 0

_stroke = (0, 0, 0)
_fill = None
_strokeWeight = 1
_textSize = 12
_zorder = 1


BLACK = "#000000"
WHITE = "#FFFFFF"
RED = "#FF0000"
GREEN = "#00FF00"
BLUE = "#0000FF"
YELLOW = "#FFFF00"
CYAN = "#00FFFF"
MAGENTA = "#FF00FF"


def _set_background(ax, color):
    if hasattr(ax, "set_facecolor"):
        ax.set_facecolor(color)
    elif hasattr(ax, "set_axis_bgcolor"):
        ax.set_axis_bgcolor(color)


def _refresh():
    if _fig is None:
        return

    try:
        _fig.canvas.draw_idle()
    except Exception:
        try:
            _fig.canvas.draw()
        except Exception:
            pass

    try:
        _fig.canvas.flush_events()
    except Exception:
        pass

    try:
        plt.draw()
    except Exception:
        pass

    # Sous ancien Jupyter inline, display(fig) force le rendu
    # de la figure même si elle a été créée dans une cellule précédente.
    if display is not None:
        try:
            display(_fig)
            return
        except Exception:
            pass

    try:
        plt.show()
    except Exception:
        pass


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


def size(w, h):
    global _fig, _ax
    global width, height
    global _zorder

    width = w
    height = h
    _zorder = 1

    plt.close("all")

    # Processing : size(w, h) correspond à w x h pixels.
    # Matplotlib exprime figsize en pouces : pixels = pouces * dpi.
    dpi = 100.0
    figsize = (float(w) / dpi, float(h) / dpi)

    _fig, _ax = plt.subplots(
        figsize=figsize,
        dpi=dpi
    )

    # La zone de dessin occupe exactement toute la figure,
    # sans marges Matplotlib autour du canevas.
    _fig.subplots_adjust(
        left=0,
        right=1,
        bottom=0,
        top=1
    )

    _ax.set_xlim(0, width)
    _ax.set_ylim(height, 0)
    _ax.set_aspect("equal")
    _ax.axis("off")

    _set_background(_ax, "white")

    if hasattr(_fig.patch, "set_facecolor"):
        _fig.patch.set_facecolor("white")

    _refresh()


def background(c):
    color = _color(c)

    _set_background(_ax, color)

    if hasattr(_fig.patch, "set_facecolor"):
        _fig.patch.set_facecolor(color)

    _refresh()


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

    _refresh()


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

    _refresh()


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
    _refresh()


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
    _refresh()


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
    _refresh()


def square(x, y, s):
    rect(x, y, s, s)


def triangle(x1, y1, x2, y2, x3, y3):
    edge = _stroke if _stroke is not None else "none"
    face = _fill if _fill is not None else "none"

    shape = Polygon(
        [(x1, y1), (x2, y2), (x3, y3)],
        closed=True,
        edgecolor=edge,
        facecolor=face,
        linewidth=_strokeWeight,
        zorder=_next_zorder()
    )

    _ax.add_patch(shape)
    _refresh()


def arc(x, y, w, h, start, stop):
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
    _refresh()


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

    _refresh()


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

    _set_background(_ax, "white")

    _zorder = 1
    _refresh()


def save(filename):
    if _fig is None:
        return

    # Conserve exactement les dimensions définies par size().
    _fig.savefig(
        filename,
        dpi=_fig.dpi
    )
