# Desarrollo experimental del núcleo de Milán

Esta rama amplía el intérprete inicial en Python. **No es todavía un compilador ni un núcleo Rust.**

## Novedades

- Palabras clave equivalentes en español e inglés: `si/if`, `sino/else`, `mientras/while`, `para/for`, `en/in`, `funcion/function`, `devolver/return`, `mostrar/print`.
- Booleanos `verdadero/falso` y `true/false`.
- Acceso a elementos de listas por índice, por ejemplo `datos[0]`.
- Pruebas adicionales y ejecución automatizada propuesta mediante GitHub Actions.

## Uso

```bash
python3 milan.py examples/bilingue.milan
python3 -m unittest discover -s tests -v
```

## Limitaciones

La ejecución continúa utilizando un subconjunto de Python. No existe aún un analizador propio, compatibilidad de indentación, sistema de módulos, gestor de paquetes ni compilación nativa. **No es una sandbox segura para código no confiable.** No se ha verificado todavía el resultado de la ejecución en CI.

## Siguiente trabajo

Estabilizar los tests, mejorar diagnósticos con líneas de origen, separar el analizador del motor y diseñar la gramática formal antes de migrar a Rust.
