# Milán

> La única limitación es tu imaginación.

Milán es un lenguaje de programación gratuito y abierto bajo licencia MIT. Puedes mezclar español e inglés en el mismo programa. Esta rama contiene la candidata **1.0.0-rc.1**.

## Primer programa

Guarda este código como `saludar.milan`.

```milan
nombre = "Mundo"

funcion saludar(persona) {
    mostrar("Hola", persona)
}

saludar(nombre)
```

Instala Python 3.10 o posterior y descarga el repositorio. Desde su carpeta, ejecuta `python3 milan.py examples/saludar.milan` en Linux o macOS, o `py -3 milan.py examples/saludar.milan` en Windows. Verás `Hola Mundo`. El intérprete usa la biblioteca estándar de Python.

En VS Code, instala el VSIX de Milán, abre la carpeta de tu proyecto y pulsa **Ejecutar archivo actual** en un archivo `.milan`. La extensión incluye el intérprete y detecta Python.

- [Instalación y ejecución](docs/ejecutar.md)
- [Referencia bilingüe](docs/lenguaje.md)
- [Ejemplos](examples/)
- [Extensión de VS Code](vscode-milan/README.md)
- [Pruebas](tests/README.md)
- [Cambios y trabajo pendiente](CHANGELOG.md)
