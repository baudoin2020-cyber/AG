"""
processing_lite.py
-------------------
Mini-module reprenant les noms de fonctions EXACTS de Processing (Java)
pour les figures geometriques et les I/O de fichiers, utilisable directement
dans un notebook Jupyter (rendu via matplotlib).

Conventions Processing :
- Origine (0, 0) en haut a gauche du canvas.
- Couleurs en RGB, composantes 0-255 (ou niveau de gris si un seul argument).
- Etat courant de fill/stroke, modifie par fill()/stroke()/noFill()/noStroke().

Usage typique dans un notebook :

    from processing_lite import *

    size(400, 300)
    background(240)
    fill(255, 0, 0)
    stroke(0)
    rect(50, 50, 100, 80)
    ellipse(250, 150, 120, 120)

    beginShape()
    vertex(50, 200)
    vertex(100, 250)
    vertex(20, 250)
    endShape(CLOSE)

Avec le backend inline de Jupyter (%matplotlib inline), la figure s'affiche
automatiquement a la fin de la cellule.
"""

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches


# ---------------------------------------------------------------------------
# Constantes Processing utilisees ici
# ---------------------------------------------------------------------------

CLOSE = "CLOSE"


# ---------------------------------------------------------------------------
# Etat global du canvas (comme les variables globales implicites de Processing)
# ---------------------------------------------------------------------------

_state = {
    "fig": None,
    "ax": None,
    "width": 400,
    "height": 400,
    "fill_color": (255, 255, 255),
    "fill_on": True,
    "stroke_color": (0, 0, 0),
    "stroke_on": True,
    "stroke_weight": 1.0,
    "shape_points": None,  # utilise entre beginShape() et endShape()
}


def _to_rgb(*args):
    """Convertit une couleur en tuple RGB normalise 0-1 pour matplotlib.
    Accepte :
    - 1 argument numerique (niveau de gris 0-255)
    - 3 ou 4 arguments numeriques (RGB ou RGBA 0-255, alpha ignore)
    - 1 chaine : code hexa ('#7ED321' ou '7ED321') ou nom de couleur
      reconnu par matplotlib ('red', 'skyblue', ...)
    """
    if len(args) == 1 and isinstance(args[0], str):
        s = args[0]
        if not s.startswith("#"):
            try:
                import matplotlib.colors as mcolors
                return mcolors.to_rgb(s)
            except ValueError:
                s = "#" + s  # on tente comme hexa sans le '#'
        s = s.lstrip("#")
        r = int(s[0:2], 16) / 255
        g = int(s[2:4], 16) / 255
        b = int(s[4:6], 16) / 255
        return (r, g, b)
    if len(args) == 1:
        v = args[0] / 255
        return (v, v, v)
    r, g, b = args[0] / 255, args[1] / 255, args[2] / 255
    return (r, g, b)


def _face_edge():
    face = _state["fill_color"] if _state["fill_on"] else "none"
    edge = _state["stroke_color"] if _state["stroke_on"] else "none"
    lw = _state["stroke_weight"] if _state["stroke_on"] else 0
    return face, edge, lw


# ---------------------------------------------------------------------------
# Cycle de vie du canvas : size(), background(), save()
# ---------------------------------------------------------------------------

def size(width=400, height=400):
    """Definit la taille du canvas (equivalent de size() appele dans setup())."""
    _state["width"] = width
    _state["height"] = height
    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)  # y croit vers le bas, comme dans Processing
    ax.set_aspect("equal")
    ax.axis("off")
    _state["fig"] = fig
    _state["ax"] = ax
    return fig, ax


def background(*args):
    """Remplit tout le canvas d'une couleur."""
    ax = _state["ax"]
    color = _to_rgb(*args)
    ax.add_patch(patches.Rectangle(
        (0, 0), _state["width"], _state["height"], facecolor=color, edgecolor=None, zorder=0
    ))


def save(filename):
    """Sauvegarde le canvas courant dans un fichier image (png, svg, ...)."""
    _state["fig"].savefig(filename, bbox_inches="tight", pad_inches=0)


# ---------------------------------------------------------------------------
# Etat de style : fill(), noFill(), stroke(), noStroke(), strokeWeight()
# ---------------------------------------------------------------------------

def fill(*args):
    """Definit la couleur de remplissage des formes suivantes."""
    _state["fill_color"] = _to_rgb(*args)
    _state["fill_on"] = True


def noFill():
    """Desactive le remplissage des formes suivantes."""
    _state["fill_on"] = False


def stroke(*args):
    """Definit la couleur de contour des formes suivantes."""
    _state["stroke_color"] = _to_rgb(*args)
    _state["stroke_on"] = True


def noStroke():
    """Desactive le contour des formes suivantes."""
    _state["stroke_on"] = False


def strokeWeight(w):
    """Definit l'epaisseur du contour."""
    _state["stroke_weight"] = w


# ---------------------------------------------------------------------------
# Formes geometriques : point, line, triangle, quad, rect, ellipse, circle, arc
# ---------------------------------------------------------------------------

def point(x, y):
    """Dessine un point en (x, y)."""
    ax = _state["ax"]
    color = _state["stroke_color"] if _state["stroke_on"] else _state["fill_color"]
    ax.plot([x], [y], marker="o", markersize=max(1, _state["stroke_weight"] * 2), color=color)


def line(x1, y1, x2, y2):
    """Dessine une ligne entre (x1, y1) et (x2, y2)."""
    ax = _state["ax"]
    color = _state["stroke_color"] if _state["stroke_on"] else _state["fill_color"]
    ax.plot([x1, x2], [y1, y2], color=color, linewidth=_state["stroke_weight"])


def triangle(x1, y1, x2, y2, x3, y3):
    """Dessine un triangle a partir de ses 3 sommets."""
    ax = _state["ax"]
    face, edge, lw = _face_edge()
    ax.add_patch(patches.Polygon(
        [(x1, y1), (x2, y2), (x3, y3)], closed=True, facecolor=face, edgecolor=edge, linewidth=lw
    ))


def quad(x1, y1, x2, y2, x3, y3, x4, y4):
    """Dessine un quadrilatere a partir de ses 4 sommets."""
    ax = _state["ax"]
    face, edge, lw = _face_edge()
    ax.add_patch(patches.Polygon(
        [(x1, y1), (x2, y2), (x3, y3), (x4, y4)], closed=True,
        facecolor=face, edgecolor=edge, linewidth=lw
    ))


def rect(x, y, w, h):
    """Dessine un rectangle : coin haut-gauche (x, y), largeur w, hauteur h."""
    ax = _state["ax"]
    face, edge, lw = _face_edge()
    ax.add_patch(patches.Rectangle((x, y), w, h, facecolor=face, edgecolor=edge, linewidth=lw))


def ellipse(x, y, w, h):
    """Dessine une ellipse centree en (x, y), de largeur w et hauteur h."""
    ax = _state["ax"]
    face, edge, lw = _face_edge()
    ax.add_patch(patches.Ellipse((x, y), w, h, facecolor=face, edgecolor=edge, linewidth=lw))


def circle(x, y, d):
    """Dessine un cercle centre en (x, y) de diametre d."""
    ellipse(x, y, d, d)


def arc(x, y, w, h, start, stop):
    """Dessine un arc dans l'ellipse englobante (x, y, w, h), entre les angles
    start et stop en radians (comme en Processing)."""
    import math
    ax = _state["ax"]
    face, edge, lw = _face_edge()
    ax.add_patch(patches.Arc(
        (x, y), w, h, theta1=math.degrees(start), theta2=math.degrees(stop),
        edgecolor=edge if edge != "none" else _state["fill_color"], linewidth=lw or 1
    ))


# ---------------------------------------------------------------------------
# Polygones libres : beginShape(), vertex(), endShape()
# ---------------------------------------------------------------------------

def beginShape():
    """Demarre la definition d'une forme libre (polygone)."""
    _state["shape_points"] = []


def vertex(x, y):
    """Ajoute un sommet a la forme en cours (entre beginShape() et endShape())."""
    if _state["shape_points"] is None:
        raise RuntimeError("vertex() doit etre appele entre beginShape() et endShape()")
    _state["shape_points"].append((x, y))


def endShape(mode=None):
    """Termine et dessine la forme libre. mode=CLOSE ferme le contour, comme
    en Processing."""
    ax = _state["ax"]
    points = _state["shape_points"] or []
    closed = (mode == CLOSE)
    face, edge, lw = _face_edge()
    if closed:
        ax.add_patch(patches.Polygon(points, closed=True, facecolor=face, edgecolor=edge, linewidth=lw))
    else:
        xs, ys = zip(*points) if points else ([], [])
        ax.plot(xs, ys, color=edge if edge != "none" else _state["fill_color"], linewidth=lw or 1)
    _state["shape_points"] = None


# ---------------------------------------------------------------------------
# I/O fichiers : loadStrings, saveStrings, loadJSONObject, saveJSONObject, listFiles
# ---------------------------------------------------------------------------

def loadStrings(filename):
    """Lit un fichier texte et renvoie une liste de lignes (sans \\n)."""
    with open(filename, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f]


def saveStrings(filename, strings):
    """Ecrit une liste de chaines dans un fichier texte, une par ligne."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(strings))


def loadJSONObject(filename):
    """Charge un fichier JSON et renvoie un dict Python."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def saveJSONObject(json_obj, filename, indent=2):
    """Sauvegarde un objet Python dans un fichier JSON.
    Ordre des arguments (json_obj, filename) conforme a Processing."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(json_obj, f, indent=indent, ensure_ascii=False)


def listFiles(path, extension=None):
    """Liste les fichiers d'un dossier, filtres par extension si precisee
    (ex: extension='.txt')."""
    p = Path(path)
    files = [str(f) for f in p.iterdir() if f.is_file()]
    if extension:
        files = [f for f in files if f.endswith(extension)]
    return sorted(files)
