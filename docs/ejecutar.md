# Ejecutar Milán

1. Instala Python 3.10 o posterior.
2. Descarga el código o clona la rama de la candidata.
3. Abre una terminal en la carpeta del proyecto.

```bash
git clone -b feat/milan-herramientas https://github.com/Dirix24/Lenguaje-Milan.git
cd Lenguaje-Milan
python3 milan.py examples/saludar.milan
python3 milan.py examples/resumen.milan
```

En Windows, usa `py -3` en lugar de `python3`. También puedes copiar `milan.py` a otra carpeta y pasarle la ruta de tu programa.

`python3 milan.py --check programa.milan` revisa sintaxis y módulos sin ejecutar el programa. Los errores indican el archivo y la línea cuando corresponden a una instrucción. La opción `--json` emite un objeto en stderr con `message`, `line` y `source`. La opción `--check --stdin` lee código del editor o de una tubería. Si también recibe una ruta, usa esa ruta para ubicar los módulos.

## Entrada y archivos

`entrada("Pregunta: ")` (también `input`) lee una línea de la terminal. Para probar el ejemplo interactivo con archivos, crea un directorio vacío y ejecuta:

```bash
mkdir datos
python3 milan.py --files datos examples/nota.milan
```

La escritura crea `datos/nota.txt`. Para repetir el ejemplo, usa otro directorio vacío o retira manualmente el archivo anterior.

## Permisos y límites

- Ejecuta programas de confianza. El intérprete usa Python como motor y carece de aislamiento de procesos y cuotas de tiempo o memoria.
- El programa puede incluir módulos `.milan` en su mismo directorio. Revisa también esos módulos antes de ejecutar.
- Leer y escribir archivos de datos exige autorizar un directorio existente con `--files`. Usa un directorio bajo tu control, sin acceso de escritura para terceros. La política de archivos presupone que terceros no pueden sustituir el directorio ni manipular sus entradas durante la ejecución. Pueden crearse, leerse y actualizarse archivos de texto UTF‑8 regulares. Si dos programas actualizan el mismo archivo, prevalece la última escritura. Se rechazan rutas, enlaces y nombres de dispositivo de Windows.
- La extensión ejecuta sin acceso a archivos de datos. Para usar `--files`, ejecuta el programa desde una terminal.

## Instalar el comando y probar las tareas en MX Linux

Desde la carpeta del repositorio, crea un entorno virtual e instala la candidata:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
mkdir -p datos
milan --files datos examples/tareas.milan
```

Si falta el módulo de entornos virtuales, instala el paquete `python3-venv` de MX Linux. Las tareas se guardan en `datos/tareas.json` y aparecen al abrir el programa de nuevo. Con el entorno activado, puedes usar `milan` desde cualquier carpeta. También puedes ejecutar el ejemplo con `python3 milan.py --files datos examples/tareas.milan`.
