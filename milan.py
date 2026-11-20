"""Intérprete inicial de Milán. Ejecuta un subconjunto deliberadamente limitado."""
import ast
import io
import re
import sys
import tokenize
from pathlib import Path

class MilanError(Exception):
    pass

KEYWORDS = {"verdadero": "True", "falso": "False", "y": "and", "o": "or", "no": "not", "true": "True", "false": "False"}
HEADER = [
    (re.compile(r"si\s+(.+)"), lambda m: "if " + m[1] + ":"),
    (re.compile(r"sino\s+si\s+(.+)"), lambda m: "elif " + m[1] + ":"),
    (re.compile(r"(?:sino|else)"), lambda m: "else:"),
    (re.compile(r"mientras\s+(.+)"), lambda m: "while " + m[1] + ":"),
    (re.compile(r"para\s+([a-zA-Z_][\w]*)\s+en\s+(.+)"), lambda m: "for " + m[1] + " in " + m[2] + ":"),
    (re.compile(r"funcion\s+([a-zA-Z_][\w]*)\s*\(([^()]*)\)"), lambda m: "def " + m[1] + "(" + m[2] + "):"),
]

def translate_words(source):
    tokens = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.NAME:
                token = token._replace(string=KEYWORDS.get(token.string, token.string))
            tokens.append(token)
        return tokenize.untokenize(tokens)
    except tokenize.TokenError as exc:
        raise MilanError(f"Expresión incompleta: {exc}") from exc

def compile_milan(source):
    output, depth = [], 0
    for number, raw in enumerate(source.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Una llave de cierre puede compartir línea con 'sino'.
        if line.startswith("}"):
            depth -= 1
            if depth < 0:
                raise MilanError(f"Línea {number}: llave de cierre inesperada")
            line = line[1:].strip()
            if not line:
                continue
        opens = line.endswith("{")
        if opens:
            line = line[:-1].strip()
            match = next((fn(m) for regex, fn in HEADER if (m := regex.fullmatch(line))), None)
            if match is None:
                raise MilanError(f"Línea {number}: bloque desconocido: {line}")
            line = match
        elif "{" in line or "}" in line:
            raise MilanError(f"Línea {number}: las llaves deben delimitar bloques")
        if not opens and re.match(r"^(si|sino|mientras|para|funcion)\b", line):
            raise MilanError(f"Línea {number}: falta '{{' en el bloque")
        line = re.sub(r"^devolver\b", "return", line)
        line = re.sub(r"^mostrar\s*\(", "print(", line)
        output.append("    " * depth + translate_words(line))
        if opens:
            depth += 1
    if depth:
        raise MilanError("Faltan llaves de cierre")
    return "\n".join(output) + "\n"

ALLOWED = (
    ast.Module, ast.Expr, ast.Assign, ast.Name, ast.Load, ast.Store,
    ast.Constant, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd, ast.Not, ast.And, ast.Or, ast.Eq, ast.NotEq,
    ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.If, ast.While, ast.For,
    ast.List, ast.Tuple, ast.Call, ast.FunctionDef, ast.arguments,\n    ast.Subscript, ast.Slice,
    ast.arg, ast.Return, ast.Pass,
)
BUILTINS = {"print": print, "range": range, "len": len}
FORBIDDEN = set(dir(__builtins__)) | {"eval", "exec", "open", "input", "__builtins__"}

def validate(tree):
    functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED):
            raise MilanError(f"Construcción no admitida: {type(node).__name__}")
        if isinstance(node, ast.Name) and (node.id.startswith("_") or node.id in FORBIDDEN - set(BUILTINS)):
            raise MilanError(f"Nombre no permitido: {node.id}")
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith("_") or node.name in FORBIDDEN:
                raise MilanError(f"Función no permitida: {node.name}")
            if node.decorator_list or node.returns or getattr(node, "type_params", []):
                raise MilanError("Decoradores y anotaciones no admitidos")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in (set(BUILTINS) | functions) or node.keywords:
                raise MilanError("Solo se permiten llamadas a funciones de Milán y funciones básicas")
        if isinstance(node, ast.Assign) and any(not isinstance(t, ast.Name) for t in node.targets):
            raise MilanError("Solo se admiten asignaciones a variables")
        if isinstance(node, ast.For) and not isinstance(node.target, ast.Name):
            raise MilanError("El bucle requiere una variable")
    return tree

def execute(source):
    translated = compile_milan(source)
    try:
        tree = ast.parse(translated, filename="<milan>")
        validate(tree)
        exec(compile(tree, "<milan>", "exec"), {"__builtins__": BUILTINS}, {})
    except (SyntaxError, TypeError, NameError, ZeroDivisionError, RecursionError, IndexError, ValueError, OverflowError) as exc:
        raise MilanError(str(exc)) from exc

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 milan.py archivo.milan", file=sys.stderr)
        return 2
    try:
        execute(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (MilanError, OSError) as exc:
        print(f"Error de Milán: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
