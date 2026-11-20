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


class TestHerramientas(unittest.TestCase):
    def test_collections_conversion_and_recovery(self):
        source = '''
datos = {"n": [entero("4"), float("2.5")]}
append(datos["n"], 9)
datos["n"][0] = 7
print(pop(datos["n"]), desde_json(to_json(datos))["n"][0])
try {
    decimal("error")
} capturar {
    mostrar("recuperado")
}
'''
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            execute(source)
        self.assertEqual(output.getvalue(), "9 7\nrecuperado\n")

    def test_missing_key_diagnostic(self):
        with self.assertRaisesRegex(MilanError, "Línea 2: Clave ausente"):
            execute('datos = {}\nmostrar(datos["ausente"])')

    def test_update_needs_permission_and_existing_file(self):
        source = 'update_file("datos.txt", "nuevo")'
        with self.assertRaisesRegex(MilanError, "--files"):
            execute(source)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "datos.txt"
            with self.assertRaises(MilanError):
                execute(source, files_root=tmp)
            self.assertFalse(path.exists())
            path.write_text("original", encoding="utf-8")
            execute(source, files_root=tmp)
            self.assertEqual(path.read_text(encoding="utf-8"), "nuevo")
            self.assertEqual(list(Path(tmp).iterdir()), [path])

    def test_update_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "datos"
            root.mkdir()
            target = Path(tmp) / "fuera.txt"
            target.write_text("original", encoding="utf-8")
            try:
                (root / "datos.txt").symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("El entorno no permite crear enlaces simbólicos")
            with self.assertRaisesRegex(MilanError, "sin enlaces"):
                execute('update_file("datos.txt", "nuevo")', files_root=root)
            self.assertEqual(target.read_text(encoding="utf-8"), "original")

    def test_example_survives_multiple_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            cli = [sys.executable, str(ROOT / "milan.py"), "--files", tmp,
                   str(ROOT / "examples" / "tareas.milan")]
            for inputs, expected in (
                ("2\nComprar pan\n0\n", [{"titulo": "Comprar pan", "hecha": False}]),
                ("3\nhola\n3\n1\n0\n", [{"titulo": "Comprar pan", "hecha": True}]),
                ("4\n1\n0\n", []),
            ):
                result = subprocess.run(cli, input=inputs, text=True, encoding="utf-8",
                                        capture_output=True, timeout=10,
                                        env=dict(os.environ, PYTHONUTF8="1"))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads((Path(tmp) / "tareas.json").read_text(
                    encoding="utf-8")), expected)
