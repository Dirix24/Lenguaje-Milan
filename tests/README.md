# Pruebas

Desde la raíz, ejecuta `python3 -m unittest discover -s tests -v` (en Windows, `py -3 -m unittest discover -s tests -v`). Las pruebas cubren el intérprete, la CLI, ejemplos, ámbitos, preservación de cadenas, módulos y permisos de archivos.

Con Node.js, ejecuta `node --test tests/test_extension.js` para comprobar las llamadas al intérprete y a la terminal con una API de VS Code simulada. GitHub Actions repite las pruebas de Python en los tres sistemas y genera un VSIX verificando su contenido.
