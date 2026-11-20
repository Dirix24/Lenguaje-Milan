"""Intérprete y CLI de Milán."""
import argparse
import ast
import builtins
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path


class MilanError(Exception):
    def __init__(self, message, line=None, source=None):
        super().__init__(message)
        self.line = line
        self.source = source

    def __str__(self):
        location = f"Línea {self.line}: " if self.line else ""
        return (f"{self.source}: " if self.source else "") + location + super().__str__()


WORDS = {
    "si": "if", "sino": "else", "mientras": "while", "para": "for",
    "en": "in", "funcion": "def", "function": "def", "devolver": "return",
    "verdadero": "True", "falso": "False", "true": "True", "false": "False",
    "y": "and", "o": "or", "no": "not",
    "intentar": "try", "capturar": "except", "romper": "break", "continuar": "continue",
}
HEADERS = {"if", "elif", "else", "while", "for", "def", "try", "except"}
# Cada cadena es un solo token. Las llaves y los comentarios se reconocen fuera de ella.
TOKEN = re.compile(r"""\s+|\#.*|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\w+|.""")
STRING_PREFIXES = {"b", "br", "f", "fr", "r", "rb", "rf", "u", "t", "tr", "rt"}


def compile_milan(source):
    output = []
    blocks = []
    for number, raw in enumerate(source.split("\n"), 1):
        significant = []
        delimiters = []
        previous_end = 0
        for token in TOKEN.finditer(raw):
            value = token[0]
            if value.startswith("#"):
                break
            if value.isspace():
                continue
            if value in {"'", '"'}:
                raise MilanError("Falta cerrar una cadena de texto", number)
            if value[0] in {"'", '"'} and (
                raw.startswith(value[0] * 3, token.start())
                or (significant and token.start() == previous_end
                    and significant[-1][0].lower() in STRING_PREFIXES)
            ):
                raise MilanError("Usa cadenas simples o dobles sin prefijos", number)
            if value in {";", "\\"}:
                raise MilanError("Escribe una instrucción por línea", number)
            if value in {"(", "["}:
                delimiters.append(value)
            if value in {")", "]"}:
                if not delimiters or delimiters.pop() != {")": "(", "]": "["}[value]:
                    raise MilanError(f"Cierre inesperado: {value}", number)
            significant.append(token)
            previous_end = token.end()
        if delimiters:
            raise MilanError(f"Falta cerrar '{delimiters[-1]}' en esta línea", number)
        tokens = [token[0] for token in significant]

        if tokens and tokens[0] == "}":
            if not blocks:
                raise MilanError("Llave de cierre inesperada", number)
            blocks.pop()
            tokens.pop(0)
            significant.pop(0)
        if not tokens:
            output.append("")
            continue

        # Sustituye los tokens en el texto original para conservar operadores como >= y //.
        opens = tokens[-1] == "{"
        if opens:
            tokens.pop()
        if not tokens:
            raise MilanError("Falta la cabecera del bloque", number)
        if tokens[0] in {"intentar", "try", "capturar", "except"} and len(tokens) != 1:
            raise MilanError("Usa intentar o capturar sin argumentos", number)

        translated = [WORDS.get(token, token) for token in tokens]
        if translated[:2] == ["else", "if"]:
            translated[:2] = ["elif", ""]
        header = translated[0] in HEADERS
        if header and not opens:
            raise MilanError("Falta '{' para abrir el bloque", number)
        if opens and not header:
            raise MilanError("Se esperaba si, sino, mientras, para, funcion, intentar o capturar antes de '{'", number)

        parts = []
        start = significant[0].start()
        for token, replacement in zip(significant, translated):
            parts.extend((raw[start:token.start()], replacement))
            start = token.end()
        output.append("    " * len(blocks) + "".join(parts).rstrip() + (":" if opens else ""))
        if opens:
            blocks.append(number)
    if blocks:
        raise MilanError("Falta '}' para cerrar el bloque", blocks[-1])
    return "\n".join(output) + "\n"


ALLOWED = (
    ast.Module, ast.Expr, ast.Assign, ast.Name, ast.Load, ast.Store,
    ast.Constant, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd, ast.Not, ast.And, ast.Or, ast.Eq, ast.NotEq,
    ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.If, ast.While, ast.For,
    ast.List, ast.Tuple, ast.Call, ast.FunctionDef, ast.arguments,
    ast.Subscript, ast.Slice, ast.arg, ast.Return, ast.Pass,
    ast.Dict, ast.Try, ast.ExceptHandler, ast.Break, ast.Continue, ast.In, ast.NotIn,
)


def append_item(items, value):
    if not isinstance(items, list):
        raise TypeError("agregar requiere una lista")
    items.append(value)


def pop_item(items, index=-1):
    if not isinstance(items, list):
        raise TypeError("quitar requiere una lista")
    return items.pop(index)


def to_json(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


BASIC = {
    "print": print, "mostrar": print, "range": range, "rango": range,
    "len": len, "longitud": len, "input": input, "entrada": input,
    "entero": int, "int": int, "decimal": float, "float": float,
    "agregar": append_item, "append": append_item, "quitar": pop_item, "pop": pop_item,
    "recortar": str.strip, "trim": str.strip,
    "minusculas": str.lower, "lower": str.lower,
    "mayusculas": str.upper, "upper": str.upper,
    "dividir": str.split, "split": str.split, "unir": str.join, "join": str.join,
    "a_json": to_json, "to_json": to_json, "desde_json": json.loads, "from_json": json.loads,
}
INCLUDE_NAMES = {"incluir", "include"}
CAPABILITIES = INCLUDE_NAMES | {"leer_archivo", "read_file", "escribir_archivo", "write_file", "actualizar_archivo", "update_file"}
RESERVED = set(dir(builtins)) | CAPABILITIES | BASIC.keys() | WORDS.keys()


def validate(tree):
    includes = {
        statement.value for statement in tree.body
        if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call)
        and isinstance(statement.value.func, ast.Name)
        and statement.value.func.id in INCLUDE_NAMES
    }
    include_targets = {call.func for call in includes}
    for node in ast.walk(tree):
        line = getattr(node, "lineno", None)
        if not isinstance(node, ALLOWED):
            raise MilanError(f"Construcción no admitida: {type(node).__name__}", line)
        if isinstance(node, (ast.Name, ast.arg, ast.FunctionDef)):
            name = node.id if isinstance(node, ast.Name) else (
                node.arg if isinstance(node, ast.arg) else node.name
            )
            allowed_read = isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and (
                name in BASIC or name in CAPABILITIES - INCLUDE_NAMES or node in include_targets
            )
            if name.startswith("_") or (name in RESERVED and not allowed_read):
                raise MilanError(f"Nombre reservado: {name}", line)
        if isinstance(node, ast.Constant) and type(node.value) not in (str, int, float, bool):
            raise MilanError("Valor literal no admitido", line)
        if isinstance(node, ast.FunctionDef):
            args = node.args
            if (node.decorator_list or node.returns or getattr(node, "type_params", [])
                or args.posonlyargs or args.vararg or args.kwonlyargs or args.kwarg
                or args.defaults or any(arg.annotation for arg in args.args)):
                raise MilanError("Usa parámetros simples sin valores predeterminados", line)
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.keywords:
                raise MilanError("Usa una función con argumentos posicionales", line)
            if node.func.id in INCLUDE_NAMES and (
                node not in includes or len(node.args) != 1
                or not isinstance(node.args[0], ast.Constant)
                or not isinstance(node.args[0].value, str)
            ):
                raise MilanError('Escribe incluir("archivo.milan") en el nivel principal', line)
        if isinstance(node, ast.Assign) and any(
            not isinstance(target, (ast.Name, ast.Subscript)) for target in node.targets
        ):
            raise MilanError("Asigna a una variable, un índice o una clave", line)
        if isinstance(node, ast.Dict) and None in node.keys:
            raise MilanError("Escribe pares de clave y valor en el diccionario", line)
        if isinstance(node, ast.Try) and (
            node.orelse or node.finalbody or len(node.handlers) != 1
        ):
            raise MilanError("Usa un solo bloque capturar después de intentar", line)
        if isinstance(node, ast.ExceptHandler) and (node.type is not None or node.name):
            raise MilanError("Usa capturar sin argumentos", line)
        if isinstance(node, ast.For) and (not isinstance(node.target, ast.Name) or node.orelse):
            raise MilanError("Usa una variable en el bucle para y reserva sino para si", line)
        if isinstance(node, ast.While) and node.orelse:
            raise MilanError("Reserva sino para si", line)
    return includes


def prepare(source, filename):
    try:
        tree = ast.parse(compile_milan(source), filename=filename)
        includes = validate(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                node.type = ast.copy_location(ast.Name(id="_errores_milan", ctx=ast.Load()), node)
        return compile(tree, filename, "exec"), includes
    except SyntaxError as exc:
        loop_errors = {
            "'break' outside loop": "Usa romper o break dentro de un bucle",
            "'continue' not properly in loop": "Usa continuar o continue dentro de un bucle",
        }
        message = loop_errors.get(exc.msg, f"Sintaxis inválida ({exc.msg})")
        raise MilanError(message, exc.lineno, filename) from exc
    except (ValueError, RecursionError) as exc:
        raise MilanError("El código contiene una expresión inválida o demasiado compleja",
                         source=filename) from exc
    except MilanError as exc:
        if not exc.source:
            exc.source = filename
        raise


SAFE_FILENAME = re.compile(r"[\w-][\w.-]*", re.UNICODE)
WINDOWS_DEVICES = re.compile(r"(?:CON|PRN|AUX|NUL|COM[0-9¹²³]|LPT[0-9¹²³])", re.I)


def local_file(root, name):
    if (not isinstance(name, str) or not SAFE_FILENAME.fullmatch(name)
        or name.endswith(".") or WINDOWS_DEVICES.fullmatch(name.split(".")[0])):
        raise MilanError("Usa un nombre de archivo simple, sin rutas ni nombres de dispositivo")
    path = root / name
    if path.is_symlink() or path.resolve().parent != root:
        raise MilanError("El archivo debe estar dentro del directorio autorizado y sin enlaces")
    return path


def read_text(path):
    # O_NOFOLLOW bloquea enlaces en la apertura donde está disponible.
    flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
             | getattr(os, "O_BINARY", 0))
    if not path.is_file():
        raise MilanError(f"Se esperaba un archivo normal: {path.name}")
    with os.fdopen(os.open(path, flags), "r", encoding="utf-8") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink > 1:
            raise MilanError(f"Se esperaba un archivo normal: {path.name}")
        return stream.read()


RECOVERABLE_ERRORS = (MilanError, TypeError, ArithmeticError, IndexError, KeyError,
                      ValueError, OSError, EOFError)
RUNTIME_ERRORS = RECOVERABLE_ERRORS + (NameError, RecursionError)


def execute(source, *, source_path=None, files_root=None, check=False):
    path = Path(source_path).resolve() if source_path is not None else None
    root = path.parent if path else None
    files = Path(files_root).resolve() if files_root is not None else None
    if files is not None and not files.is_dir():
        raise MilanError("El directorio autorizado para archivos debe existir")
    programs = {}
    active = set()
    filenames = set()

    def load(text, filename):
        active.add(filename)
        filenames.add(filename)
        code, includes = prepare(text, filename)
        for call in sorted(includes, key=lambda item: item.lineno):
            name = call.args[0].value
            try:
                if root is None or not name.endswith(".milan"):
                    raise MilanError("Los módulos deben ser archivos .milan junto al programa")
                module = local_file(root, name)
                module_filename = str(module.resolve())
                if module_filename in active:
                    raise MilanError(f"Inclusión circular: {name}")
                if name not in programs:
                    programs[name] = load(read_text(module), module_filename)
            except (MilanError, OSError, ValueError, RecursionError) as exc:
                if isinstance(exc, MilanError) and exc.source:
                    raise
                raise MilanError(str(exc), call.lineno, filename) from exc
        active.remove(filename)
        return code

    code = load(source, str(path) if path else "<milan>")
    if check:
        return

    def data_path(name):
        if files is None:
            raise MilanError("El acceso a datos requiere --files DIRECTORIO")
        return local_file(files, name)

    def read_file(name):
        return read_text(data_path(name))

    def write_file(name, content):
        path = data_path(name)
        if not isinstance(content, str):
            raise MilanError("El contenido del archivo debe ser texto")
        with path.open("x", encoding="utf-8", newline="") as stream:
            stream.write(content)

    def update_file(name, content):
        path = data_path(name)
        if not isinstance(content, str):
            raise MilanError("El contenido del archivo debe ser texto")
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink > 1:
            raise MilanError("Actualiza un archivo normal sin enlaces")
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="", dir=files, delete=False
            ) as stream:
                temporary = Path(stream.name)
                stream.write(content)
            temporary.chmod(stat.S_IMODE(info.st_mode))
            temporary.replace(path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    included = set()

    def include(name):
        if name not in included:
            included.add(name)
            exec(programs[name], environment, environment)

    environment = {"__builtins__": {
        **BASIC, "_errores_milan": RECOVERABLE_ERRORS,
        "incluir": include, "include": include,
        "leer_archivo": read_file, "read_file": read_file,
        "escribir_archivo": write_file, "write_file": write_file,
        "actualizar_archivo": update_file, "update_file": update_file,
    }}
    try:
        exec(code, environment, environment)
    except RUNTIME_ERRORS as exc:
        frame = exc.__traceback__
        filename, line = None, None
        while frame:
            candidate = frame.tb_frame.f_code.co_filename
            if candidate in filenames:
                filename, line = candidate, frame.tb_lineno
            frame = frame.tb_next
        explanations = {
            NameError: "Variable o función sin definir",
            ZeroDivisionError: "No se puede dividir entre cero",
            IndexError: "Índice fuera de la lista o el texto",
            KeyError: "Clave ausente en el diccionario",
            TypeError: "Revisa los tipos de los valores y los argumentos",
            EOFError: "No hay más datos de entrada",
            RecursionError: "Hay demasiadas llamadas anidadas",
        }
        message = explanations.get(type(exc))
        raise MilanError(f"{message} ({exc})" if message else str(exc), line, filename) from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ejecuta o revisa programas Milán.")
    parser.add_argument("--check", action="store_true", help="Revisa sin ejecutar")
    parser.add_argument("--json", action="store_true", help="Emite diagnósticos JSON en stderr")
    parser.add_argument("--stdin", action="store_true", help="Lee el código de stdin con --check")
    parser.add_argument("--files", type=Path, metavar="DIRECTORIO", help="Habilita archivos de datos")
    parser.add_argument("archivo", type=Path, nargs="?")
    args = parser.parse_args(argv)
    if (args.stdin and not args.check) or (not args.stdin and args.archivo is None):
        parser.error("Indica un archivo, o usa --check --stdin")
    try:
        source = sys.stdin.read() if args.stdin else args.archivo.read_text(encoding="utf-8-sig")
        execute(source, source_path=args.archivo, files_root=args.files, check=args.check)
    except (MilanError, OSError, ValueError) as exc:
        if args.json:
            print(json.dumps({"message": exc.args[0] if isinstance(exc, MilanError) else str(exc),
                              "line": getattr(exc, "line", None),
                              "source": getattr(exc, "source", None)}), file=sys.stderr)
        else:
            print(f"Error de Milán: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
