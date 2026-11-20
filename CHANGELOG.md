# Cambios de Milán

## 1.1.0-rc.1

- Añade conversiones numéricas, edición de listas, diccionarios y conversión JSON.
- Añade bloques bilingües de recuperación de errores y actualización de archivos con permisos explícitos.
- Instala el comando `milan` y añade un programa de tareas persistentes.

## 1.0.0-rc.1

- Corrige las cabeceras bilingües, conserva las cadenas al traducir y localiza los errores en el archivo y línea originales.
- Añade entrada interactiva, creación y lectura de archivos UTF-8 con permiso explícito, y módulos locales con revisión previa y detección de ciclos.
- La extensión incluye el intérprete, sugerencias, coloreado, diagnósticos sin ejecución y un comando de terminal con argumentos directos.
- Añade pruebas del núcleo y de la extensión, CI en Linux, Windows y macOS y generación del VSIX.

### Límites de la candidata

- Los módulos comparten variables globales. Los nombres de módulo son literales y sus archivos viven en el directorio del programa.
- Se documenta un conjunto pequeño de sintaxis. Las formas accidentales heredadas de Python, como parámetros predeterminados, prefijos de cadenas y continuación de líneas, quedan fuera para mantener una gramática enseñable y consistente.
- La revisión en el editor comprueba la sintaxis y las inclusiones. Los errores de valores se muestran durante la ejecución.
- Ejecuta programas de confianza. El motor carece de aislamiento y límites de recursos.
- Se aplazan espacios de nombres de módulos, gestor de paquetes, compilación nativa, WebAssembly, Milán Studio e integración con bibliotecas externas.

## 0.2 experimental

- Añade equivalencias bilingües, listas indexadas y pruebas iniciales.
