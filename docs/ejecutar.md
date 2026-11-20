# Ejecutar Milán

Milán dispone de un intérprete experimental implementado en Python 3.10 o superior.

Desde la raíz del repositorio:

```bash
python3 milan.py examples/hola.milan
python3 milan.py examples/funciones.milan
python3 -m unittest discover -s tests -v
```

## Funciones iniciales

- Variables, números, cadenas, booleanos y listas.
- `mostrar(...)` para imprimir.
- `si`, `sino`, `sino si` y `mientras`.
- `para variable en lista { ... }`.
- `funcion nombre(argumentos) { ... }` y `devolver`.
- Operaciones aritméticas y comparaciones.
- `verdadero`, `falso`, `y`, `o`, `no`.

## Limitaciones

Esta es una implementación experimental y no es un entorno aislado para ejecutar código no confiable. Usa un subconjunto de Python como motor interno. No admite módulos, clases, acceso a atributos ni entrada de usuario. El bucle `mientras` puede no terminar si su condición nunca cambia.
