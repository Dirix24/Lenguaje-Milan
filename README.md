# 🇪🇸 Milán — Un lenguaje, muchas posibilidades

> **La única limitación es tu imaginación.**

**Milán** es un proyecto comunitario de lenguaje de programación universal, gratuito y de código abierto. Su propósito es reunir capacidades habituales de diferentes ecosistemas en una experiencia coherente, fácil de aprender y suficientemente potente para el desarrollo profesional.

**Estado actual: prototipo experimental 0.1.x.** El intérprete inicial está implementado en Python. Las características descritas como *visión* o *planificadas* aún no están disponibles. El objetivo no es prometer que Milán reemplazará por completo a todos los lenguajes, sino reducir la necesidad de aprender varias sintaxis para tareas comunes.

## Principios

- **Un núcleo abierto:** el lenguaje y sus herramientas fundamentales deben poder usarse sin registro, pagos, editor obligatorio ni IA.
- **Aprender sin barreras innecesarias:** documentación clara, ejemplos progresivos, errores comprensibles y diseño inclusivo, también para personas con TDAH o dificultades de aprendizaje. No se presupone una única forma de aprender.
- **Sencillo al empezar, potente al crecer:** tipos inferidos por defecto y anotaciones opcionales; estilos de programación avanzados disponibles progresivamente.
- **Español e inglés:** palabras clave equivalentes, mezcla en un mismo archivo y futura herramienta de traducción.
- **Ecosistema interoperable:** bibliotecas propias y puentes con otros lenguajes, comenzando por Python.
- **Seguridad y transparencia:** permisos explícitos para operaciones sensibles, aislamiento cuando sea posible y cambios propuestos por IA sujetos a aprobación.

## ¿Qué funciona hoy?

El repositorio contiene un intérprete experimental `milan.py` basado en Python, ejemplos `.milan` y pruebas iniciales. Su diseño actual incluye traducción de palabras clave y un subconjunto limitado de expresiones, asignaciones, condiciones, bucles y funciones. **No se ha establecido todavía una compatibilidad completa ni una suite de pruebas verificada en todos los sistemas.** No ejecutes código no confiable: el intérprete experimental no constituye una sandbox de seguridad.

### Primer programa

```milan
nombre = "Ana"
mostrar("Hola " + nombre)

funcion sumar(a, b) {
    devolver a + b
}

mostrar(sumar(5, 3))
```

### Ejecutar el prototipo

Requiere Python 3.10 o superior. Desde la raíz del repositorio:

```bash
python3 milan.py examples/hola.milan
python3 milan.py examples/funciones.milan
python3 -m unittest discover -s tests -v
```

Consulta [la guía de ejecución](docs/ejecutar.md) para conocer las limitaciones. El código de ejemplo no implica que estén disponibles todas las características futuras.

## Visión del lenguaje (todavía no implementada completamente)

### Sintaxis flexible y bilingüe

Se quiere admitir español e inglés combinados en el mismo programa, con traducción de palabras clave y bloques tanto con llaves como con indentación, siempre que las reglas sean inequívocas.

```milan
# Ejemplo conceptual de sintaxis bilingüe futura
funcion saludar(nombre) {
    print("Hola " + nombre)
}
saludar("Milán")
```

Se prevén alternativas sencillas a la sintaxis clásica cuando no generen ambigüedad. Los ejemplos conceptuales **no son una garantía de ejecución en el intérprete actual**.

### Tipos y paradigmas

- Inferencia de tipos por defecto y anotaciones explícitas opcionales.
- Funciones, objetos, programación funcional y asincronía, enseñados de manera progresiva.
- Memoria automática por defecto, con mecanismos avanzados de control cuando estén bien definidos.
- Concurrencia accesible para principiantes y opciones de bajo nivel para profesionales.

### Ejecución y rendimiento

El camino propuesto comienza con un prototipo en Python y avanza hacia un núcleo propio en **Rust**. Se estudiarán tecnologías como **LLVM** para compilación nativa y **WebAssembly** para entornos compatibles, conservando un modo interpretado. El objetivo es ofrecer un modo sencillo y otro optimizado; no se prometen velocidades concretas.

### Bibliotecas y plataformas

Milán aspira a servir para web, aplicaciones, videojuegos, IA, servidores, automatización y sistemas mediante bibliotecas y herramientas específicas. Se priorizarán puentes con Python y, más adelante, JavaScript y bibliotecas nativas. Se buscará compatibilidad progresiva con Linux, Windows, macOS, Android, iOS y web, respetando las restricciones de cada plataforma.

## Milán Studio y otros editores (planificado)

Milán **no dependerá de un editor concreto**. La visión incluye:

- Milán Studio, editor propio con perfiles de accesibilidad, colores y tipografías personalizables, navegación por teclado y modo sin distracciones.
- Extensiones y soporte para VS Code, VSCodium, Neovim y otros editores, según la comunidad contribuya.
- Errores en modo principiante (explicaciones y soluciones) y profesional (detalles técnicos).
- Depuración y aprendizaje interactivos con tutoriales, ejercicios y ejemplos visuales.
- Gestor de paquetes por comandos y catálogo visual.

## Inteligencia artificial opcional (planificada)

Se desea integrar ayuda para comprender, generar y depurar código, y APIs sencillas para crear aplicaciones con IA. Se estudiarán modelos locales y servicios externos. Un agente podrá **proponer** archivos, cambios y pruebas, pero deberá solicitar aprobación antes de modificar el proyecto. Las funciones básicas del lenguaje deberán funcionar sin IA y, en la medida de lo posible, sin conexión.

## Hoja de ruta

Consulta [ROADMAP.md](ROADMAP.md). Las versiones y etapas son propuestas, no fechas ni funciones ya publicadas.

## Comunidad y contribuciones

Milán está pensado para que cualquier persona pueda **usar, estudiar, modificar y mejorar su núcleo abierto**. Son bienvenidas contribuciones de código, pruebas, documentación, accesibilidad, traducciones y ejemplos. Consulta [CONTRIBUTING.md](CONTRIBUTING.md). Las decisiones técnicas deben priorizar compatibilidad, claridad, seguridad y mantenimiento.

## Licencia

El proyecto utiliza la [licencia MIT](LICENSE). La licencia permite reutilización y modificación bajo sus condiciones. Los componentes de terceros conservan sus propias licencias.

---

**Milán: un lenguaje, muchas posibilidades. La única limitación es tu imaginación.**
