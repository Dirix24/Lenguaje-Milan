# Hoja de ruta de Milán

> Plan orientativo de desarrollo. No representa funcionalidades ya implementadas ni fechas de entrega.

## Criterios del proyecto

1. El núcleo del lenguaje será abierto, gratuito y utilizable sin IA ni editor obligatorio.
2. Cada etapa deberá acompañarse de pruebas, ejemplos, documentación y criterios de aceptación.
3. Se priorizará un intérprete fiable antes de añadir compilación, IDE o compatibilidad masiva.
4. Las versiones 0.x podrán introducir cambios incompatibles documentados. La versión 1.0 aspirará a reglas estables y compatibilidad definida.
5. Las propuestas de IA deberán requerir consentimiento antes de modificar archivos.

## Etapas propuestas

| Versión orientativa | Objetivo | Criterios de aceptación |
| --- | --- | --- |
| 0.1.x | Consolidar intérprete inicial | Ejecutar los ejemplos básicos; errores controlados; pruebas automatizadas reproducibles |
| 0.2.x | Listas, archivos y módulos | Especificación mínima; permisos de archivos; pruebas de importación y errores |
| 0.3.x | Sintaxis bilingüe y flexible | Equivalencias español/inglés; llaves e indentación sin ambigüedad; traductor de palabras clave |
| 0.4.x | Paquetes e interoperabilidad inicial | Gestor mínimo y puente documentado con Python |
| 0.5.x | Núcleo experimental en Rust | Analizador y ejecutor propios; pruebas de compatibilidad con el prototipo |
| 0.6–0.9 | Compilación, seguridad y herramientas | Evaluar LLVM, WebAssembly, concurrencia, extensiones y primeras herramientas educativas |
| 1.0 | Primera versión estable | Especificación publicada, suite de compatibilidad y política de versiones |

## Líneas de trabajo paralelas, cuando el núcleo lo permita

- **Lenguaje:** sintaxis, tipos, memoria, ejecución, concurrencia y APIs estándar.
- **Herramientas:** editor independiente, extensiones, gestor de paquetes y depuración.
- **Accesibilidad:** modos de errores, lectura y navegación, personalización, enseñanza inclusiva.
- **IA opcional:** asistencia local/remota, permisos, revisión humana y privacidad.
- **Comunidad:** guías de contribución, pruebas multiplataforma, traducciones y gobernanza abierta.

## Plataformas objetivo

Linux, Windows y macOS como sistemas de escritorio; web y plataformas móviles de forma progresiva. No se garantiza compatibilidad hasta que haya implementaciones y pruebas específicas.

## Estado y seguimiento

El prototipo actual se encuentra en una fase experimental. Cada característica debe documentarse como **implementada**, **en desarrollo** o **propuesta**. Las prioridades podrán ajustarse a los resultados de pruebas y contribuciones de la comunidad.
