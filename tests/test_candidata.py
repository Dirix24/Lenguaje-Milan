import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from milan import MilanError, execute

ROOT = Path(__file__).resolve().parents[1]


class CandidateTests(unittest.TestCase):
    def output(self, source, **kwargs):
        result = io.StringIO()
        with contextlib.redirect_stdout(result):
            execute(source, **kwargs)
        return result.getvalue()

    def test_greeting_from_request(self):
        self.assertEqual(self.output((ROOT / "examples" / "saludar.milan").read_text(
            encoding="utf-8")), "Hola Mundo\n")

    def test_nested_functions_lexical_scope_and_recursion(self):
        source = """base = 2
function outer(value) {
    base = 3
    funcion power(n) {
        if n == 0 {
            devolver value
        }
        return base * power(n - 1)
    }
    return power(2)
}
mostrar(outer(5), base)
"""
        self.assertEqual(self.output(source), "45 2\n")
        with self.assertRaisesRegex(MilanError, "sin definir"):
            self.output(source + "power(1)")

    def test_bilingual_operators_and_blocks(self):
        source = """datos = [10, 20, 30]
if falso {
    mostrar(0)
} sino if no false and datos[1] >= 20 {
    para n in datos[1:] {
        print(n // 10)
    }
} else {
    print(0)
}
contador = 1
while contador < 3 {
    contador = contador + 1
}
mostrar(contador ** 2 % 4)
"""
        self.assertEqual(self.output(source), "2\n3\n1\n")

    def test_strings_are_opaque(self):
        source = r'''
si verdadero { # false {
    mostrar("si y true { } # <> ;", 'function no falso', "hola \"mundo\"")
}
'''
        self.assertEqual(self.output(source), 'si y true { } # <> ; function no falso hola "mundo"\n')

    def test_line_numbers_point_to_original_source(self):
        for source, line, message in (
            ("# comentario\n\nsi verdadero {\nmostrar(1 / 0)\n}", 4, "dividir"),
            ("\nmostrar([1][2])", 2, "Índice"),
            ("\nmostrar('abc)", 2, "cadena"),
            ("si verdadero {\nmostrar(1)\n# falta la llave", 1, "cerrar el bloque"),
            ("\nmostrar((1).__class__)", 2, "Attribute"),
            ("\nsi verdadero\nmostrar(1)", 2, "abrir el bloque"),
        ):
            with self.subTest(source=source):
                with self.assertRaisesRegex(MilanError, message) as caught:
                    execute(source)
                self.assertEqual(caught.exception.line, line)

    def test_file_capability_creates_and_reads_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = 'write_file("salida.txt", "Milán")\nmostrar(leer_archivo("salida.txt"))'
            with self.assertRaisesRegex(MilanError, "--files"):
                execute(source)
            self.assertEqual(self.output(source, files_root=tmp), "Milán\n")
            with self.assertRaises(MilanError):
                execute('escribir_archivo("salida.txt", "otro")', files_root=tmp)
            self.assertEqual((Path(tmp) / "salida.txt").read_text(encoding="utf-8"), "Milán")

    def test_file_paths_cannot_leave_root_or_target_devices(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("../outside.txt", "/outside.txt", "C:/outside.txt", "a:b", "NUL.txt",
                         r"a\b.txt", "file.txt."):
                with self.subTest(name=name), self.assertRaisesRegex(MilanError, "nombre de archivo"):
                    execute(f'write_file({json.dumps(name)}, "texto")', files_root=tmp)

    def test_file_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "data"
            root.mkdir()
            outside = Path(tmp) / "outside.txt"
            outside.write_text("secreto")
            try:
                (root / "link.txt").symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("El entorno no permite crear enlaces simbólicos")
            with self.assertRaisesRegex(MilanError, "sin enlaces"):
                execute('read_file("link.txt")', files_root=root)

    def test_module_preflight_execution_and_source_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = root / "helper.milan"
            entry = root / "entrada.milan"
            source = 'include("helper.milan")\nincluir("helper.milan")\nprint(doble(4))'
            module.write_text('mostrar("cargado")\nfuncion doble(n) {\nreturn n * 2\n}', encoding="utf-8")
            self.assertEqual(self.output(source, source_path=entry, check=True), "")
            self.assertEqual(self.output(source, source_path=entry), "cargado\n8\n")
            module.write_text('\nmostrar(1 / 0)', encoding="utf-8")
            with self.assertRaises(MilanError) as caught:
                execute(source, source_path=entry)
            self.assertEqual(caught.exception.source, str(module.resolve()))
            self.assertEqual(caught.exception.line, 2)
            module.write_text('incluir("helper.milan")', encoding="utf-8")
            with self.assertRaisesRegex(MilanError, "circular"):
                execute(source, source_path=entry, check=True)

    def test_module_directive_cannot_be_called_indirectly_or_inside_blocks(self):
        for code in ("alias = include", 'include(entrada())',
                     'if true {\ninclude("uno.milan")\n}'):
            with self.subTest(code=code), self.assertRaises(MilanError):
                execute(code, check=True)

    def test_cli_input_and_check_without_execution(self):
        env = dict(os.environ, PYTHONUTF8="1")
        with tempfile.TemporaryDirectory() as tmp:
            program = Path(tmp) / "programa Milán.milan"
            program.write_text('nombre = entrada("Nombre: ")\nmostrar("Hola", nombre)', encoding="utf-8")
            cli = [sys.executable, str(ROOT / "milan.py")]
            run = subprocess.run([*cli, str(program)], input="Inés\n", text=True, encoding="utf-8",
                                 capture_output=True, env=env, timeout=10)
            self.assertEqual((run.returncode, run.stdout, run.stderr), (0, "Nombre: Hola Inés\n", ""))
            check = subprocess.run([*cli, "--check", "--json", "--stdin", str(program)],
                                   input="\nsi verdadero\nmostrar(1)", text=True, encoding="utf-8",
                                   capture_output=True, env=env, timeout=10)
            self.assertEqual(check.returncode, 1)
            self.assertEqual(json.loads(check.stderr)["line"], 2)
            self.assertEqual(check.stdout, "")

    def test_check_has_no_file_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            execute('write_file("salida.txt", "Milán")', files_root=tmp, check=True)
            self.assertFalse((Path(tmp) / "salida.txt").exists())
