import contextlib
import io
import unittest
from pathlib import Path

from milan import MilanError, execute

ROOT = Path(__file__).resolve().parents[1]

class TestMilan(unittest.TestCase):
    def run_milan(self, source):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            execute(source)
        return output.getvalue().strip()

    def test_examples(self):
        expected = {
            "hola.milan": "Hola",
            "variables.milan": "Ana\n20\nTrue",
            "condiciones.milan": "Eres mayor de edad",
            "bucles.milan": "1\n2\n3\n4\n5",
            "funciones.milan": "8",
        }
        for name, result in expected.items():
            with self.subTest(name=name):
                actual = self.run_milan((ROOT / "examples" / name).read_text(encoding="utf-8"))
                self.assertIn(result, actual)

    def test_while(self):
        self.assertEqual(self.run_milan("x = 0\nmientras x < 3 {\nmostrar(x)\nx = x + 1\n}"), "0\n1\n2")

    def test_strings_preserve_keywords(self):
        self.assertEqual(self.run_milan('mostrar("verdadero y falso")'), "verdadero y falso")

    def test_reject_import(self):
        with self.assertRaises(MilanError):
            self.run_milan("import os")

    def test_reject_attribute_access(self):
        with self.assertRaises(MilanError):
            self.run_milan('mostrar((1).__class__)')

    def test_unclosed_block(self):
        with self.assertRaises(MilanError):
            self.run_milan("si verdadero {\nmostrar(1)")

if __name__ == "__main__":
    unittest.main()
