import re
from pathlib import Path

PROCESSING_RUNNER_VERSION = "2026-11-05-04"

# ============================================================
# BOUCLES for
# ============================================================

_MOTS_FLOAT = r'(?:\d*\.\d|\d\.|\bPI\b|\bTWO_PI\b|\bHALF_PI\b|\bQUARTER_PI\b|\bTAU\b)'


def _est_float(expr, variables_float):
    if re.search(_MOTS_FLOAT, expr):
        return True
    return any(
        re.search(r'\b' + re.escape(v) + r'\b', expr)
        for v in variables_float
    )


def _for_en_while(init, cond, maj):
    # for (init; cond; maj) { corps }  ->  init / while cond: corps ; maj
    debut = (init + '\n') if init else ''
    return (
        debut
        + '\x01' + maj + '\x01'
        + 'while ' + (cond if cond else 'True') + ':'
    )


def _sortir_increments(ligne):

    if re.match(r'\s*for\s*\(', ligne):
        return ligne

    # Instruction seule (i++; ou ++i;) : rien a faire ici
    if re.fullmatch(r'\s*(\+\+|--)?\w+(\+\+|--)?\s*;?\s*\}?\s*', ligne):
        return ligne

    apres, avant = [], []

    def post(m):
        apres.append(m.group(1) + (' += 1' if m.group(2) == '++' else ' -= 1'))
        return m.group(1)

    def pre(m):
        avant.append(m.group(2) + (' += 1' if m.group(1) == '++' else ' -= 1'))
        return m.group(2)

    nouvelle = re.sub(r'\b(\w+)(\+\+|--)(?!\s*[;)]?\s*$)', post, ligne)
    nouvelle = re.sub(r'(\+\+|--)(\w+)\b', pre, nouvelle)

    if not apres and not avant:
        return ligne

    m = re.match(r'(\s*)(.*?)(;?)(\s*\}?\s*)$', nouvelle)
    indent, corps, _, fin = m.groups()
    morceaux = avant + [corps] + apres
    return indent + '; '.join(morceaux) + ';' + fin


def _convertir_for(m, warnings, variables_float=()):

    texte = m.group(0)
    parties = m.group(1).split(';')

    if len(parties) != 3:
        warnings.append("Boucle for non convertie : " + texte)
        return texte

    init, cond, maj = (p.strip() for p in parties)

    mi = re.fullmatch(
        r'(?:(int|float|double|long)\s+)?(\w+)\s*=\s*(.+)', init
    )
    if not mi:
        return _for_en_while(init, cond, maj)

    type_var, var, debut = mi.group(1), mi.group(2), mi.group(3).strip()
    v = re.escape(var)

    # Boucle sur des nombres a virgule : range() n'accepte que des
    # entiers, on ecrit donc une boucle while. La mise a jour est
    # placee en fin de bloc (marqueur \x01...\x01, traite lors du
    # passage accolades -> indentation).
    if (
        type_var in ('float', 'double')
        or var in variables_float
        or _est_float(debut + ' ' + cond + ' ' + maj, variables_float)
    ):
        return (
            var + ' = ' + debut + '\n'
            + '\x01' + maj + '\x01'
            + 'while ' + cond + ':'
        )

    mc = re.fullmatch(v + r'\s*(<=|<|>=|>)\s*(.+)', cond)
    if not mc:
        # Condition autre que "i < fin" (ex. i*pas < c) : boucle while
        return _for_en_while(init, cond, maj)

    op, fin = mc.group(1), mc.group(2).strip()

    pas = None
    for motif, signe in (
        (v + r'\s*\+\+|\+\+\s*' + v, '+1'),
        (v + r'\s*--|--\s*' + v, '-1'),
        (v + r'\s*\+=\s*(.+)', '+'),
        (v + r'\s*-=\s*(.+)', '-'),
        (v + r'\s*=\s*' + v + r'\s*\+\s*(.+)', '+'),
        (v + r'\s*=\s*' + v + r'\s*-\s*(.+)', '-'),
    ):
        mm = re.fullmatch(motif, maj)
        if mm:
            if signe == '+1':
                pas = '1'
            elif signe == '-1':
                pas = '-1'
            elif signe == '+':
                pas = mm.group(1).strip()
            else:
                pas = '-' + mm.group(1).strip()
                if not re.fullmatch(r'-\w+', pas):
                    pas = '-(' + mm.group(1).strip() + ')'
            break

    if pas is None:
        return _for_en_while(init, cond, maj)

    croissant = not pas.startswith('-')

    if (op in ('<', '<=')) != croissant:
        warnings.append(
            "Boucle for : sens du pas incoherent avec la condition : "
            + texte
        )

    # Division entre entiers : en Java step/2 reste un entier.
    def entier(e):
        return 'int(' + e + ')' if '/' in e else e

    debut, fin, pas = entier(debut), entier(fin), entier(pas)

    if op in ('<=', '>='):
        decalage = 1 if op == '<=' else -1
        if re.fullmatch(r'-?\d+', fin):
            fin = str(int(fin) + decalage)
        else:
            fin = fin + (' + 1' if decalage == 1 else ' - 1')

    if pas == '1':
        return 'for ' + var + ' in range(' + debut + ', ' + fin + '):'

    return (
        'for ' + var + ' in range('
        + debut + ', ' + fin + ', ' + pas + '):'
    )


# ============================================================
# PROCESSING JAVA -> PROCESSING PYTHON
# ============================================================

def convert_processing_text(code):

    warnings = []

    # --------------------------------------------------------
    # Commentaires
    # --------------------------------------------------------

    # Nombres a virgule : 0.5f -> 0.5, 2f -> 2
    code = re.sub(
        r'(?<![\w#.])(\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)[fFdD]\b',
        r'\1',
        code
    )

    # Variables declarees float/double (pour les boucles for)
    variables_float = set(
        re.findall(r'\b(?:float|double)\s+(\w+)\s*[=;,)]', code)
    )
    for groupe in re.findall(
        r'\b(?:float|double)\s+(\w+(?:\s*,\s*\w+)+)\s*;', code
    ):
        variables_float.update(v.strip() for v in groupe.split(','))

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

    # for (int i = 0; i < 10; i++) { ... }
    # for (int y = 3; y < 486; y = y + 23) { ... }
    # for (x = 50; x <= 1200; x += 250) line(...);   (sans accolades)
    # for (int i = 10; i > 0; i--) { ... }
    #   -> for i in range(debut, fin, pas):

    # Incrementation dans une expression : text(num++, x, y);
    #   -> text(num, x, y); num += 1   (et ++num : avant l'instruction)
    code = '\n'.join(
        _sortir_increments(ligne) for ligne in code.split('\n')
    )

    # Boucle sur une seule ligne, sans accolades : on ajoute les accolades.
    code = re.sub(
        r'(for\s*\((?:[^()]|\([^()]*\))*\))[ \t]*(?![ \t]*\{)([^\n{};]+;)',
        r'\1 {\n\2\n}',
        code
    )

    code = re.sub(
        r'for\s*\(((?:[^()]|\([^()]*\))*)\)\s*\{',
        lambda m: _convertir_for(m, warnings, variables_float),
        code
    )

    # --------------------------------------------------------
    # Conversions de type : (int) random(100) -> int(random(100))
    # --------------------------------------------------------

    code = re.sub(
        r'\(\s*(int|float)\s*\)\s*'
        r'(\w+\s*\((?:[^()]|\([^()]*\))*\)|\w+(?:\.\w+)?)',
        r'\1(\2)',
        code
    )

    # --------------------------------------------------------
    # Declarations multiples : int a, b, c; -> a = b = c = None
    # --------------------------------------------------------

    code = re.sub(
        r'\b(?:int|float|double|long|boolean|char|byte|short|String|color)'
        r'\s+(\w+(?:\s*,\s*\w+)+)\s*;',
        lambda m: ' = '.join(
            v.strip() for v in m.group(1).split(',')
        ) + ' = None;',
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

    # int x = a / b;  -> x = int(a / b)   (division entiere de Java)
    code = re.sub(
        r'\b(?:int|long|short|byte)\s+(\w+)\s*=\s*([^;\n]*/[^;\n]*);',
        r'\1 = int(\2);',
        code
    )

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
    pile = []   # mise a jour a ecrire en fin de bloc (boucles while)

    def fermer():
        nonlocal indent
        maj = pile.pop() if pile else None
        if maj:
            result.append('    ' * indent + maj)
        indent = max(0, indent - 1)

    for raw_line in code.splitlines():

        line = raw_line.strip()

        if not line:
            result.append('')
            continue

        # Accolade fermante au début
        while line.startswith('}'):

            fermer()
            line = line[1:].strip()

        maj_bloc = None
        mm = re.match(r'\x01(.*?)\x01(.*)$', line)
        if mm:
            maj_bloc = mm.group(1).strip().rstrip(';')
            line = mm.group(2).strip()

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
            pile.append(maj_bloc)

        if closes:
            fermer()

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
#         # nom dans le code Java : (couleur, gris en %, nom en gris)
#         "BLEU_CLAIR": ("#DFEAF7", "15%", "FOND"),
#         "BLEU":       ("#003366", "70%", "REMPLISSAGE"),
#         "ORANGE":     ("#FF7A00", "50%", "TRAIT1"),
#         "VERT":       ("#7ED321", "30%", "TRAIT2"),
#     }
#
# Le 3e element (facultatif) est le nom de la variable dans les codes
# en niveaux de gris ; sans lui, le nom d'origine est garde.
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

        if not isinstance(valeur, (tuple, list)) or len(valeur) not in (2, 3):
            raise ValueError(
                nom + " : il faut (couleur, gris en %, nom en gris), "
                "par exemple ('#003366', '70%', 'REMPLISSAGE')."
            )

        couleur, gris = valeur[0], valeur[1]
        nom_gris = valeur[2] if len(valeur) == 3 else nom

        if not re.fullmatch(r"[A-Za-z_]\w*", str(nom_gris)):
            raise ValueError(
                nom + " : nom en gris invalide " + repr(nom_gris)
            )
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

        propre[nom] = (couleur.upper(), _gris_vers_255(gris), nom_gris)

    noms_gris = [v[2] for v in propre.values()]
    if len(set(noms_gris)) != len(noms_gris):
        raise ValueError("Deux couleurs ont le meme nom en gris.")

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


def _code_java_propre(code_java, palette, gris=False):
    """
    Version .pde valide pour Processing.
    Couleur : palette declaree en 'color NOM = #RRGGBB;', couleurs
              sans guillemets.
    Gris    : palette declaree en 'int FOND = 217;' (nom en gris) et
              couleurs ecrites en dur remplacees par leur niveau (0-255).
    """

    type_couleur = "int" if gris else "color"

    def valeur(nom):
        coul, g, _ = palette[nom]
        return str(g) if gris else coul

    lignes = code_java.strip("\n").splitlines()
    trouves = set()

    for i, ligne in enumerate(lignes):
        m = re.match(
            r"^(\s*)(?:int|color)\s+(\w+)\s*=\s*[^;]*;\s*$",
            ligne
        )
        if m and m.group(2) in palette:
            lignes[i] = (
                m.group(1) + type_couleur + " " + m.group(2)
                + " = " + valeur(m.group(2)) + ";"
            )
            trouves.add(m.group(2))

    manquants = [
        type_couleur + " " + nom + " = " + valeur(nom) + ";"
        for nom in palette
        if nom not in trouves
        and re.search(r"\b" + nom + r"\b", code_java)
    ]

    if manquants:
        lignes = _inserer_apres_size(lignes, manquants)

    code = "\n".join(lignes) + "\n"

    # '#DFEAF7' -> #DFEAF7 (syntaxe Processing)
    code = re.sub(r"['\"](#[0-9A-Fa-f]{6})['\"]", r"\1", code)

    if gris:
        # #DAAB3A -> 171, d'apres la luminance
        code = re.sub(
            r"(?<![\w#])(#[0-9A-Fa-f]{6})\b",
            lambda m: str(_gris_depuis_hex(m.group(1))),
            code
        )
        code = _renommer_pour_gris(code, palette)

    return code


def _renommer_pour_gris(code, palette):
    # BLEU_CLAIR -> FOND, BLEU -> REMPLISSAGE, ... (en une seule passe)
    noms = {nom: v[2] for nom, v in palette.items() if v[2] != nom}
    if not noms:
        return code
    motif = r"\b(" + "|".join(
        re.escape(n) for n in sorted(noms, key=len, reverse=True)
    ) + r")\b"
    return re.sub(motif, lambda m: noms[m.group(1)], code)


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
        "    ag2.dist = _dist\n"
        "from math import sin, cos, tan, asin, acos, atan, atan2, "
        "sqrt, pow, floor, ceil, exp, log, degrees, radians\n"
        "PI = 3.141592653589793\n"
        "TWO_PI = TAU = 2 * PI\n"
        "HALF_PI = PI / 2\n"
        "QUARTER_PI = PI / 4\n\n"
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
        code_java/<nom>.pde          code Processing Java (couleur)
        code_python/<nom>.py         code Processing Python (couleur)
        code_java_gris/<nom>.pde     code Java en niveaux de gris
        code_python_gris/<nom>.py    code Python en niveaux de gris
                                     (si niveaux_de_gris=True)

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
            ("java_gris", "code_java_gris"),
            ("python_gris", "code_python_gris"),
        )
    }

    for cle, dossier in dossiers.items():
        if cle.endswith("gris") and not niveaux_de_gris:
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
        chemins["java_gris"] = os.path.join(
            dossiers["java_gris"], nom_base + ".pde"
        )
        chemins["python_gris"] = os.path.join(
            dossiers["python_gris"], nom_base + ".py"
        )

    # --- Conversion -------------------------------------------------

    code_python, warnings = convert_processing_text(code_java)

    code_python_couleur = _appliquer_palette_python(
        code_python,
        {nom: repr(v[0]) for nom, v in palette.items()}
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
            {nom: str(v[1]) for nom, v in palette.items()}
        )

        # Couleurs ecrites en dur dans le code (hors palette) :
        # converties d'apres leur luminance.
        code_python_gris = re.sub(
            r"['\"](#[0-9A-Fa-f]{6})['\"]",
            lambda m: str(_gris_depuis_hex(m.group(1))),
            code_python_gris
        )

        with open(chemins["java_gris"], "w", encoding="utf-8") as f:
            f.write(_code_java_propre(code_java, palette, gris=True))

        code_python_gris = _renommer_pour_gris(code_python_gris, palette)

        with open(chemins["python_gris"], "w", encoding="utf-8") as f:
            f.write(code_python_gris)

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
    if niveaux_de_gris:
        print("Java gris     : " + chemins["java_gris"])
        print("Python gris   : " + chemins["python_gris"])

    return chemins
