import re
from pathlib import Path

PROCESSING_RUNNER_VERSION = "2026-11-04-02"

# ============================================================
# PROCESSING JAVA -> PROCESSING PYTHON
# ============================================================

def convert_processing_text(code):

    warnings = []

    # --------------------------------------------------------
    # Commentaires
    # --------------------------------------------------------

    code = re.sub(r'//', '#', code)
    code = re.sub(
        r'/\*([\s\S]*?)\*/',
        lambda m: '\n'.join(
            '# ' + line
            for line in m.group(1).splitlines()
        ),
        code
    )

    # --------------------------------------------------------
    # Couleurs Processing
    # --------------------------------------------------------

    # #DFEAF7 -> '#DFEAF7'
    # Ne modifie pas une couleur déjà entre guillemets.
    code = re.sub(
        r'(?<![\'"])(#[0-9A-Fa-f]{6})(?![\'"])',
        r"'\1'",
        code
    )

    # --------------------------------------------------------
    # Boucles for classiques
    # IMPORTANT : à traiter avant la suppression des types Java
    # --------------------------------------------------------

    # for (int i = 0; i < 10; i++) {
    code = re.sub(
        r'for\s*\(\s*int\s+(\w+)\s*=\s*([^;]+);'
        r'\s*\1\s*<\s*([^;]+);'
        r'\s*\1\+\+\s*\)\s*\{',
        lambda m:
            'for ' + m.group(1)
            + ' in range('
            + m.group(2).strip()
            + ', '
            + m.group(3).strip()
            + '):',
        code
    )

    # for sans "int"
    code = re.sub(
        r'for\s*\(\s*(\w+)\s*=\s*([^;]+);'
        r'\s*\1\s*<\s*([^;]+);'
        r'\s*\1\+\+\s*\)\s*\{',
        lambda m:
            'for ' + m.group(1)
            + ' in range('
            + m.group(2).strip()
            + ', '
            + m.group(3).strip()
            + '):',
        code
    )

    # --------------------------------------------------------
    # Fonctions
    # --------------------------------------------------------

    # void setup() {
    code = re.sub(
        r'void\s+(\w+)\s*\(([^)]*)\)\s*\{',
        r'def \1(\2):',
        code
    )

    # int fonction(...) {
    code = re.sub(
        r'(int|float|double|long|boolean|String|color)\s+'
        r'(\w+)\s*\(([^)]*)\)\s*\{',
        r'def \2(\3):',
        code
    )

    # --------------------------------------------------------
    # Types dans les paramètres
    # --------------------------------------------------------

    types = (
        'int|float|double|long|boolean|char|'
        'byte|short|String|color'
    )

    code = re.sub(
        r'\b(' + types + r')\s+(\w+)',
        r'\2',
        code
    )

    # --------------------------------------------------------
    # Conditions
    # --------------------------------------------------------

    code = re.sub(
        r'else\s+if\s*\((.*?)\)\s*\{',
        r'elif \1:',
        code
    )

    code = re.sub(
        r'if\s*\((.*?)\)\s*\{',
        r'if \1:',
        code
    )

    code = re.sub(
        r'else\s*\{',
        r'else:',
        code
    )

    code = re.sub(
        r'while\s*\((.*?)\)\s*\{',
        r'while \1:',
        code
    )

    # --------------------------------------------------------
    # Variables Java
    # --------------------------------------------------------

    # int x = 10;
    code = re.sub(
        r'\b(int|float|double|long|boolean|char|'
        r'byte|short|String|color)\s+(\w+)\s*=',
        r'\2 =',
        code
    )

    # int x;
    code = re.sub(
        r'\b(int|float|double|long|boolean|char|'
        r'byte|short|String|color)\s+(\w+)\s*;',
        r'\2 = None',
        code
    )

    # --------------------------------------------------------
    # Booléens
    # --------------------------------------------------------

    code = re.sub(r'\btrue\b', 'True', code)
    code = re.sub(r'\bfalse\b', 'False', code)
    code = re.sub(r'\bnull\b', 'None', code)

    # --------------------------------------------------------
    # Opérateurs
    # --------------------------------------------------------

    code = code.replace('&&', ' and ')
    code = code.replace('||', ' or ')

    code = re.sub(
        r'!(?!=)',
        'not ',
        code
    )

    code = re.sub(
        r'\b(\w+)\+\+',
        r'\1 += 1',
        code
    )

    code = re.sub(
        r'\b(\w+)--',
        r'\1 -= 1',
        code
    )

    # --------------------------------------------------------
    # Tableaux
    # --------------------------------------------------------

    code = re.sub(
        r'(int|float|double|boolean|String)\s*\[\]\s*'
        r'(\w+)\s*=\s*\{([^}]*)\}\s*;',
        r'\2 = [\3]',
        code
    )

    # tableau.length
    code = re.sub(
        r'(\w+)\.length',
        r'len(\1)',
        code
    )

    # --------------------------------------------------------
    # Fonctions Java courantes
    # --------------------------------------------------------

    code = code.replace(
        'System.out.println(',
        'println('
    )

    code = code.replace(
        'System.out.print(',
        'print('
    )

    code = code.replace(
        'Math.PI',
        'PI'
    )

    code = code.replace(
        'Math.sqrt',
        'sqrt'
    )

    code = code.replace(
        'Math.abs',
        'abs'
    )

    code = code.replace(
        'Math.pow',
        'pow'
    )

    code = code.replace(
        'Math.sin',
        'sin'
    )

    code = code.replace(
        'Math.cos',
        'cos'
    )

    # --------------------------------------------------------
    # Accolades -> indentation
    # --------------------------------------------------------

    result = []
    indent = 0

    for raw_line in code.splitlines():

        line = raw_line.strip()

        if not line:
            result.append('')
            continue

        # Accolade fermante au début
        while line.startswith('}'):

            indent = max(0, indent - 1)
            line = line[1:].strip()

        # Accolade fermante en fin
        closes = line.endswith('}')

        if closes:
            line = line[:-1].strip()

        # Supprime ;
        if line.endswith(';'):
            line = line[:-1]

        if line:
            result.append(
                '    ' * indent + line
            )

        # Ouverture d'un bloc
        if line.endswith(':'):
            indent += 1

        if closes:
            indent = max(0, indent - 1)

    code = '\n'.join(result)

    # --------------------------------------------------------
    # Avertissements
    # --------------------------------------------------------

    if re.search(r'\bclass\s+\w+', code):
        warnings.append(
            "Classe détectée : conversion manuelle probablement nécessaire."
        )

    if re.search(r'\bnew\s+', code):
        warnings.append(
            "Mot-clé 'new' détecté : vérifier la création des objets."
        )

    if re.search(r'\bPVector\b', code):
        warnings.append(
            "PVector détecté : vérifier la compatibilité Processing Python."
        )

    if re.search(r'\bPImage\b', code):
        warnings.append(
            "PImage détecté : vérifier la compatibilité Processing Python."
        )

    return code.strip() + '\n', warnings


# ============================================================
# CONVERSION D'UN FICHIER
# ============================================================

def convert_processing(
    input_file,
    output_file=None,
    show=True
):

    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(
            "Fichier introuvable : "
            + str(input_file)
        )

    source = input_file.read_text(
        encoding='utf-8'
    )

    converted, warnings = convert_processing_text(
        source
    )

    if output_file is None:
        output_file = input_file.with_suffix('.py')
    else:
        output_file = Path(output_file)

    output_file.write_text(
        converted,
        encoding='utf-8'
    )

    if show:

        print("=" * 60)
        print("SOURCE :", input_file)
        print("SORTIE :", output_file)
        print("=" * 60)
        print()
        print(converted)

        if warnings:

            print()
            print("AVERTISSEMENTS :")

            for warning in warnings:
                print(" - " + warning)

        else:

            print()
            print("OK : aucune alerte.")

    return converted, warnings


# ============================================================
# CONVERSION D'UN DOSSIER
# ============================================================

def convert_folder(folder="."):

    folder = Path(folder)

    files = list(
        folder.glob("*.pde")
    )

    if not files:

        print(
            "Aucun fichier .pde trouvé dans :",
            folder
        )

        return

    for file in files:

        print()
        print("=" * 60)
        print("CONVERSION :", file.name)
        print("=" * 60)

        convert_processing(file)


# ============================================================
# PALETTE : COULEURS ET NIVEAUX DE GRIS
# ============================================================
#
# Dans le notebook :
#
#     PALETTE = {
#         # nom utilise dans le code Java : (couleur, gris en %)
#         "BLEU_CLAIR": ("#DFEAF7", "15%"),   # fond
#         "BLEU":       ("#003366", "70%"),   # remplissage
#         "ORANGE":     ("#FF7A00", "50%"),   # trait 1
#         "VERT":       ("#7ED321", "30%"),   # trait 2
#     }
#     definir_palette(PALETTE)
#
# Les noms de la palette remplacent les declarations du code Java
# (int BLEU = '#003366'; ...). Un nom absent du code est ajoute juste
# apres size().
#
# Gris en % = taux d'encre noire (convention imprimerie) :
# 0% = blanc, 100% = noir. Les gris de la palette doivent rester
# entre GRIS_MIN et GRIS_MAX.

GRIS_MIN = 15   # %
GRIS_MAX = 70   # %

_PALETTE = {}


def _gris_vers_255(pourcentage):
    # 15% d'encre -> 217 ; 70% d'encre -> 77
    return int(round(255 * (1 - pourcentage / 100.0)))


def _verifier_palette(palette):

    propre = {}

    for nom, valeur in palette.items():

        if not re.fullmatch(r"[A-Za-z_]\w*", nom):
            raise ValueError(
                "Nom de couleur invalide : " + repr(nom)
            )

        if not isinstance(valeur, (tuple, list)) or len(valeur) != 2:
            raise ValueError(
                nom + " : il faut un couple (couleur, niveau de gris), "
                "par exemple ('#003366', 40)."
            )

        couleur, gris = valeur
        couleur = str(couleur).strip()

        if not couleur.startswith("#"):
            couleur = "#" + couleur

        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", couleur):
            raise ValueError(
                nom + " : couleur invalide " + repr(valeur[0])
                + " (format attendu '#RRGGBB')."
            )

        if isinstance(gris, str):
            gris = gris.strip().rstrip("%").strip()

        try:
            gris = float(gris)
        except (TypeError, ValueError):
            raise ValueError(
                nom + " : gris invalide " + repr(valeur[1])
                + " (exemple attendu : '40%')."
            )

        if not GRIS_MIN <= gris <= GRIS_MAX:
            raise ValueError(
                nom + " : le gris doit etre entre "
                + str(GRIS_MIN) + "% et " + str(GRIS_MAX)
                + "% (valeur donnee : " + str(valeur[1]) + ")."
            )

        propre[nom] = (couleur.upper(), _gris_vers_255(gris))

    return propre


def definir_palette(palette):
    """
    Fixe la palette utilisee par defaut par convert_and_run_and_save_image.
    palette : {nom: (couleur '#RRGGBB', gris en % entre GRIS_MIN et GRIS_MAX)}
    """

    global _PALETTE
    _PALETTE = _verifier_palette(palette)
    return dict(_PALETTE)


def _gris_depuis_hex(couleur):
    # Luminance perceptive (ITU-R BT.601), ramenee dans la plage
    # GRIS_MIN..GRIS_MAX : blanc -> GRIS_MIN, noir -> GRIS_MAX.
    r = int(couleur[1:3], 16)
    g = int(couleur[3:5], 16)
    b = int(couleur[5:7], 16)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    encre = GRIS_MIN + (GRIS_MAX - GRIS_MIN) * (1 - lum)
    return _gris_vers_255(encre)


def _inserer_apres_size(lignes, nouvelles):
    for i, ligne in enumerate(lignes):
        if re.match(r"\s*size\s*\(", ligne):
            return lignes[:i + 1] + nouvelles + lignes[i + 1:]
    return nouvelles + lignes


def _appliquer_palette_python(code_python, valeurs):
    """
    valeurs : {nom: valeur Python sous forme de texte}
    Remplace les affectations existantes, ajoute les noms manquants.
    """

    lignes = code_python.splitlines()
    trouves = set()

    for i, ligne in enumerate(lignes):
        m = re.match(r"^(\s*)(\w+)\s*=(?!=)", ligne)
        if m and m.group(2) in valeurs:
            lignes[i] = m.group(1) + m.group(2) + " = " + valeurs[m.group(2)]
            trouves.add(m.group(2))

    # On n'ajoute que les noms reellement utilises dans le code.
    manquants = [
        nom + " = " + v
        for nom, v in valeurs.items()
        if nom not in trouves
        and re.search(r"\b" + nom + r"\b", code_python)
    ]

    if manquants:
        lignes = _inserer_apres_size(lignes, manquants)

    return "\n".join(lignes) + "\n"


def _code_java_propre(code_java, palette):
    """
    Version .pde valide pour Processing : couleurs de la palette
    declarees en 'color NOM = #RRGGBB;' et couleurs sans guillemets.
    """

    lignes = code_java.strip("\n").splitlines()
    trouves = set()

    for i, ligne in enumerate(lignes):
        m = re.match(
            r"^(\s*)(?:int|color)\s+(\w+)\s*=\s*[^;]*;\s*$",
            ligne
        )
        if m and m.group(2) in palette:
            lignes[i] = (
                m.group(1) + "color " + m.group(2)
                + " = " + palette[m.group(2)][0] + ";"
            )
            trouves.add(m.group(2))

    manquants = [
        "color " + nom + " = " + coul + ";"
        for nom, (coul, _) in palette.items()
        if nom not in trouves
        and re.search(r"\b" + nom + r"\b", code_java)
    ]

    if manquants:
        lignes = _inserer_apres_size(lignes, manquants)

    code = "\n".join(lignes) + "\n"

    # '#DFEAF7' -> #DFEAF7 (syntaxe Processing)
    code = re.sub(r"['\"](#[0-9A-Fa-f]{6})['\"]", r"\1", code)

    return code


# ============================================================
# EXECUTION AVEC ag2
# ============================================================

_FONCTIONS_AG2 = (
    "size", "background", "stroke", "noStroke",
    "fill", "noFill", "strokeWeight", "point",
    "line", "circle", "ellipse", "rect", "square",
    "triangle", "arc", "textSize", "text",
    "random", "randomSeed", "clear", "dist"
)


def _preparer_pour_ag2(code_python):

    # Avec "from ag2 import *", width et height seraient copies avant
    # l'appel a size() et resteraient donc egaux a 0. On les lit
    # directement dans le module afin de toujours obtenir leur valeur
    # actualisee.
    code_python = re.sub(r"(?<![\w.])width\b", "ag2.width", code_python)
    code_python = re.sub(r"(?<![\w.])height\b", "ag2.height", code_python)

    # Appels explicites au module : on evite toute copie ou collision
    # de noms provoquee par "from ag2 import *".
    for nom_fonction in _FONCTIONS_AG2:
        code_python = re.sub(
            r"(?<![\w.])" + nom_fonction + r"\s*\(",
            "ag2." + nom_fonction + "(",
            code_python
        )

    return (
        "import ag2\n"
        "if not hasattr(ag2, 'dist'):\n"
        "    def _dist(x1, y1, x2, y2):\n"
        "        return ((x2-x1)**2 + (y2-y1)**2)**0.5\n"
        "    ag2.dist = _dist\n\n"
        + code_python
    )


def _executer_et_enregistrer(code_python, chemin_image, graine):

    import ag2

    # Meme graine pour la version couleur et la version grise :
    # les dessins aleatoires sont identiques.
    ag2.randomSeed(graine)

    programme = compile(
        _preparer_pour_ag2(code_python),
        "<code Processing converti>",
        "exec"
    )

    espace = {"__name__": "__main__"}
    exec(programme, espace, espace)

    # Fonctionne aussi avec la structure Processing setup()/draw().
    if callable(espace.get("setup")):
        espace["setup"]()

    if callable(espace.get("draw")):
        espace["draw"]()

    module_ag2 = espace.get("ag2")

    if module_ag2 is None:
        raise RuntimeError("Le module ag2.py est introuvable.")

    module_ag2.save(chemin_image)

    if not __import__("os").path.isfile(chemin_image):
        raise RuntimeError("Le dessin n'a pas ete enregistre.")

    # Evite qu'un ancien hook de ag2 reaffiche la figure.
    module_ag2._dirty = False


def _forcer_niveaux_de_gris(chemin_image):
    # Securite : toute couleur residuelle (lissage, couleur non prevue)
    # est ramenee en gris. Sans Pillow, l'image reste telle quelle.
    try:
        from PIL import Image as _PILImage
        _PILImage.open(chemin_image).convert("L").save(chemin_image)
    except ImportError:
        pass


# ============================================================
# FONCTION UNIQUE A UTILISER DANS LE NOTEBOOK
# ============================================================

def convert_and_run_and_save_image(
    code_java,
    nom_image,
    niveaux_de_gris=True,
    palette=None,
    graine=None
):
    """
    Convertit du Processing Java en Python, execute le code avec ag2.py
    et enregistre :

        images/<nom>.png         dessin en couleur
        images_gris/<nom>.png    dessin en niveaux de gris
                                 (si niveaux_de_gris=True)
        code_java/<nom>.pde      code Processing Java
        code_python/<nom>.py     code Processing Python

    palette : {nom: (couleur, gris en %)} ; par defaut celle
              fixee avec definir_palette().
    graine  : graine du hasard (tiree au sort si None) ; la meme sert
              pour les deux images.

    Exemple :
        convert_and_run_and_save_image(code_java, "grille.png")
        convert_and_run_and_save_image(code_java, "grille.png",
                                       niveaux_de_gris=False)
    """

    import os
    import random as _random

    if not isinstance(nom_image, str) or not nom_image.strip():
        raise ValueError(
            "Le nom du fichier image ne peut pas etre vide."
        )

    # Le parametre represente uniquement le nom du fichier.
    nom_image = os.path.basename(nom_image.strip())

    if not nom_image.lower().endswith(".png"):
        nom_image += ".png"

    nom_base = nom_image[:-4]

    palette = (
        _verifier_palette(palette)
        if palette is not None
        else dict(_PALETTE)
    )

    if graine is None:
        graine = _random.randrange(1, 10**9)

    racine = os.getcwd()
    dossiers = {
        cle: os.path.join(racine, nom)
        for cle, nom in (
            ("couleur", "images"),
            ("gris", "images_gris"),
            ("java", "code_java"),
            ("python", "code_python"),
        )
    }

    for cle, dossier in dossiers.items():
        if cle == "gris" and not niveaux_de_gris:
            continue
        if not os.path.isdir(dossier):
            os.makedirs(dossier)

    chemins = {
        "couleur": os.path.join(dossiers["couleur"], nom_image),
        "java": os.path.join(dossiers["java"], nom_base + ".pde"),
        "python": os.path.join(dossiers["python"], nom_base + ".py"),
    }

    if niveaux_de_gris:
        chemins["gris"] = os.path.join(dossiers["gris"], nom_image)

    # --- Conversion -------------------------------------------------

    code_python, warnings = convert_processing_text(code_java)

    code_python_couleur = _appliquer_palette_python(
        code_python,
        {nom: repr(coul) for nom, (coul, _) in palette.items()}
    )

    # --- Codes sources ------------------------------------------------

    with open(chemins["java"], "w", encoding="utf-8") as f:
        f.write(_code_java_propre(code_java, palette))

    with open(chemins["python"], "w", encoding="utf-8") as f:
        f.write(code_python_couleur)

    # --- Image en couleur --------------------------------------------

    _executer_et_enregistrer(
        code_python_couleur,
        chemins["couleur"],
        graine
    )

    # --- Image en niveaux de gris ------------------------------------

    if niveaux_de_gris:

        code_python_gris = _appliquer_palette_python(
            code_python,
            {nom: str(g) for nom, (_, g) in palette.items()}
        )

        # Couleurs ecrites en dur dans le code (hors palette) :
        # converties d'apres leur luminance.
        code_python_gris = re.sub(
            r"['\"](#[0-9A-Fa-f]{6})['\"]",
            lambda m: str(_gris_depuis_hex(m.group(1))),
            code_python_gris
        )

        _executer_et_enregistrer(
            code_python_gris,
            chemins["gris"],
            graine
        )

        _forcer_niveaux_de_gris(chemins["gris"])

    # --- Compte rendu -----------------------------------------------

    if warnings:
        print("AVERTISSEMENTS :")
        for warning in warnings:
            print(" - " + warning)

    # Dans Jupyter, affiche explicitement les fichiers qui viennent
    # d'etre enregistres.
    try:
        from IPython.display import display
        from IPython.display import Image
        display(Image(filename=chemins["couleur"]))
        if niveaux_de_gris:
            display(Image(filename=chemins["gris"]))
    except Exception:
        pass

    print("Image couleur : " + chemins["couleur"])
    if niveaux_de_gris:
        print("Image gris    : " + chemins["gris"])
    print("Code Java     : " + chemins["java"])
    print("Code Python   : " + chemins["python"])

    return chemins
