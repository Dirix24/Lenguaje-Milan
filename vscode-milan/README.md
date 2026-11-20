# Milán para Visual Studio Code

1. Instala VS Code 1.85 o posterior y Python 3.10 o posterior.
2. Descarga el VSIX de la candidata o el artefacto `milan-vsix` de GitHub Actions.
3. En VS Code, ejecuta **Extensions: Install from VSIX...** desde la paleta de comandos y selecciona el archivo `.vsix`.
4. Abre una carpeta de confianza que contenga tu programa `.milan`.
5. Pulsa el botón ▶ del editor o elige **Milán: Ejecutar archivo actual**. El programa se ejecuta en una terminal integrada que admite entrada de teclado.

La extensión incluye el intérprete, reconoce archivos `.milan` y ofrece coloreado y sugerencias de palabras en ambos idiomas. Mientras escribes, **Problemas** muestra el primer diagnóstico de sintaxis o de módulo del intérprete. Los errores que dependen de los valores aparecen en la terminal al ejecutar.

Si Python no se detecta, reinicia VS Code tras instalarlo. Puedes ajustar `milan.pythonPath` en tus preferencias de usuario e indicar el ejecutable. `milan.interpreterPath` permite seleccionar otra copia de `milan.py`. Para habilitar los archivos de datos, pasa `--files DIRECTORIO` desde la terminal.

## Crear el VSIX

Desde la carpeta `vscode-milan`, con Node.js 22 y npm:

```bash
npx --yes @vscode/vsce@3.6.2 package --no-dependencies
```

El empaquetado copia el intérprete del repositorio. Para desarrollar con una copia local, ejecuta `node prepare.js` desde esta carpeta antes de cargar la extensión.
