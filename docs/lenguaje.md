# Referencia de Milán 1.1

Escribe una instrucción por línea en UTF-8. Los bloques empiezan con `{` al final de su cabecera y terminan en una línea con `}`. La indentación es opcional. Puedes escribir `} sino {` o `} else {` en la misma línea. Fuera de una cadena, `#` inicia un comentario hasta el final de línea.

| Español | Inglés | Uso |
|---|---|---|
| `si` | `if` | `si edad >= 18 {` |
| `sino si` | `else if`, `elif` | Otra condición |
| `sino` | `else` | Alternativa final de una condición |
| `mientras` | `while` | Repite mientras la condición sea verdadera |
| `para … en` | `for … in` | Recorre una lista, texto o rango |
| `funcion` | `function` | `funcion sumar(a, b) {` |
| `devolver` | `return` | Devuelve un valor y termina la función |
| `verdadero`, `falso` | `true`, `false` | Valores booleanos |
| `y`, `o`, `no` | `and`, `or`, `not` | Operadores lógicos |
| `mostrar` | `print` | Imprime valores separados por espacios |
| `entrada` | `input` | Lee texto con un mensaje opcional |
| `rango` | `range` | Genera una secuencia de enteros |
| `longitud` | `len` | Cuenta elementos o caracteres |
| `incluir` | `include` | Incluye un módulo del directorio del programa |
| `leer_archivo` | `read_file` | Lee un archivo de texto autorizado |
| `escribir_archivo` | `write_file` | Crea un archivo de texto autorizado |

## Valores y operaciones

- Asigna con `nombre = "Ana"` o `edad = 20`. Los identificadores distinguen mayúsculas. Las palabras clave y nombres incorporados están reservados. Evita los nombres que comienzan con `_`.
- Los números pueden ser enteros o decimales. Las cadenas usan comillas simples o dobles y admiten escapes como `\n`, `\\` y `\"`. Las palabras clave escritas dentro de las cadenas se conservan. Cada cadena debe caber en una línea de origen.
- Una lista se escribe `[10, 20, 30]`. Los índices empiezan en cero. `datos[-1]` obtiene el último elemento y `datos[1:3]` obtiene una sublista. Puedes actualizar un elemento con `datos[0] = 40`.
- Aritmética: `+`, `-`, `*`, `/`, `//`, `%`, `**`. Comparaciones: `==`, `!=`, `<`, `<=`, `>`, `>=`. Usa paréntesis para agrupar. `y/and` y `o/or` evalúan el segundo operando solo cuando hace falta.
- `rango(1, 4)` recorre `1, 2, 3`. También admite `rango(fin)` y `rango(inicio, fin, paso)`.

## Funciones y ámbitos

Las funciones aceptan parámetros posicionales, pueden llamarse entre sí y pueden declararse dentro de otras funciones. Las asignaciones dentro de una función crean variables locales. Una función anidada puede leer valores de su función exterior. Coloca una definición antes de la instrucción que la llama. Si se omite el retorno, usa la llamada por su efecto, como imprimir.

```milan
function doble(numero) {
    devolver numero * 2
}

para n in [1, 2, 3] {
    if n > 1 y n < 4 {
        mostrar(doble(n))
    }
}
```

## Módulos y archivos

`incluir("herramientas.milan")` va al nivel principal y recibe un nombre literal. Los módulos viven junto al programa principal. El intérprete revisa todos antes de ejecutar, rechaza ciclos y ejecuta cada nombre una vez al llegar a su inclusión. El programa y los módulos comparten ámbito global. Elige nombres distintos para evitar que una definición reemplace a otra.

Los archivos de datos se habilitan con `--files DIRECTORIO`. `leer_archivo("nota.txt")` devuelve texto UTF-8 y `escribir_archivo("nota.txt", "Hola")` crea un archivo nuevo. Usa un nombre simple de archivo con letras, números, guiones, guiones bajos o puntos tras el primer carácter. La escritura falla cuando el nombre ya existe. Consulta [la guía de ejecución](ejecutar.md) para conocer los permisos y límites.

## Colecciones, conversión y recuperación

- Un diccionario se escribe `contacto = {"nombre": "Ana"}`. Lee o cambia un valor con `contacto["nombre"]`. Para guardar diccionarios en JSON, usa claves de texto.
- `entero/int(texto)` y `decimal/float(texto)` convierten la entrada a números. Escribe decimales con punto, como `"2.50"`.
- `agregar/append(lista, valor)` añade al final. `quitar/pop(lista, indice)` elimina y devuelve el valor. Si se omite el índice, quita el último.
- `a_json/to_json(valor)` convierte a texto JSON. `desde_json/from_json(texto)` recupera los datos.
- `intentar/try` y `capturar/except` manejan errores de datos, entrada/salida y operaciones. Los bloques se escriben sin argumentos. Los errores de sintaxis y nombres sin definir siguen apareciendo en el diagnóstico.

```milan
intentar {
    edad = entero(entrada("Edad: "))
    mostrar("El año próximo tendrás", edad + 1)
} capturar {
    mostrar("Escribe una edad en números.")
}
```

`actualizar_archivo/update_file(nombre, texto)` reemplaza el contenido de un archivo existente en el directorio de `--files`. Rechaza enlaces y escribe primero en un archivo temporal. Para crear un archivo nuevo, usa `escribir_archivo/write_file`.
