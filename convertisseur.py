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
    # Boucle for classique
    # --------------------------------------------------------

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
