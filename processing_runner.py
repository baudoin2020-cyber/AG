import re
from pathlib import Path

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
# FONCTION UNIQUE A UTILISER DANS LE NOTEBOOK
# ============================================================

def convert_and_run_and_save_image(code_java, nom_image):
    """
    Convertit du Processing Java en Python, execute le code avec ag2.py,
    puis enregistre le dessin dans le repertoire images.

    Exemple :
        convert_and_run_and_save_image(code_java, "grille.png")
    """

    import os

    if not isinstance(nom_image, str) or not nom_image.strip():
        raise ValueError(
            "Le nom du fichier image ne peut pas etre vide."
        )

    # Le parametre represente uniquement le nom du fichier.
    nom_image = os.path.basename(nom_image.strip())

    if not nom_image.lower().endswith(".png"):
        nom_image += ".png"

    dossier_images = os.path.join(
        os.getcwd(),
        "images"
    )

    if not os.path.isdir(dossier_images):
        os.makedirs(dossier_images)

    chemin_image = os.path.join(
        dossier_images,
        nom_image
    )

    code_python, warnings = convert_processing_text(
        code_java
    )

    # Avec "from ag2 import *", width et height seraient copies avant
    # l'appel a size() et resteraient donc egaux a 0. On les lit
    # directement dans le module afin de toujours obtenir leur valeur
    # actualisee.
    code_python = re.sub(
        r"(?<![\w.])width\b",
        "ag2.width",
        code_python
    )

    code_python = re.sub(
        r"(?<![\w.])height\b",
        "ag2.height",
        code_python
    )

    # Appels explicites au module : on evite toute copie ou collision
    # de noms provoquee par "from ag2 import *".
    fonctions_ag2 = (
        "size", "background", "stroke", "noStroke",
        "fill", "noFill", "strokeWeight", "point",
        "line", "circle", "ellipse", "rect", "square",
        "triangle", "arc", "textSize", "text",
        "random", "randomSeed", "clear"
    )

    for nom_fonction in fonctions_ag2:
        code_python = re.sub(
            r"(?<![\w.])"
            + nom_fonction
            + r"\s*\(",
            "ag2."
            + nom_fonction
            + "(",
            code_python
        )

    code_python = (
        "import ag2\n\n"
        + code_python
    )

    programme = compile(
        code_python,
        "<code Processing converti>",
        "exec"
    )

    espace = {
        "__name__": "__main__"
    }

    exec(programme, espace, espace)

    # Fonctionne aussi avec la structure Processing setup()/draw().
    if callable(espace.get("setup")):
        espace["setup"]()

    if callable(espace.get("draw")):
        espace["draw"]()

    module_ag2 = espace.get("ag2")

    if module_ag2 is None:
        raise RuntimeError(
            "Le module ag2.py est introuvable."
        )

    module_ag2.save(chemin_image)

    if not os.path.isfile(chemin_image):
        raise RuntimeError(
            "Le dessin n'a pas ete enregistre."
        )

    if warnings:
        print("AVERTISSEMENTS :")

        for warning in warnings:
            print(" - " + warning)

    # Dans Jupyter, affiche explicitement le fichier qui vient d'etre
    # enregistre. Cela evite qu'un ancien hook de ag2 affiche une figure
    # provenant d'une execution precedente.
    try:
        module_ag2._dirty = False

        from IPython.display import display
        from IPython.display import Image

        display(
            Image(
                filename=chemin_image
            )
        )

    except Exception:
        pass

    print(
        "Image enregistree : "
        + chemin_image
    )

    return chemin_image
