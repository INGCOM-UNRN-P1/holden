# Manual de Uso y Referencia Técnica: holden

> **HOLDEN** — Generador de mocks e inyección controlada de fallos en funciones C
> **Versión:** `0.1.0` · **CLI principal:** `holden` · **Plugin Ripley:** `mocks`

---

## 1. Arquitectura y Propósito Pedagógico

`holden` forma parte del ecosistema de herramientas de la cátedra de Programación 1 (UNRN). Su objetivo central es resolver de forma modular, determinista y automatizada las tareas asociadas a su dominio específico dentro del ciclo de desarrollo, evaluación y aprendizaje de software en C.

### Alcance Funcional (Qué cubre)
- Generación de arneses de prueba unitaria en C con aislamiento de dependencias externas.
- Síntesis de funciones de sustitución (Mocks y Stubs) a nivel de código fuente y de enlazador GNU (`ld --wrap`).
- Inyección determinista y programable de fallos de biblioteca: `malloc` retornando `NULL`, `fopen` fallando con error de archivo inexistente (`ENOENT`), o simulación de lecturas truncadas.
- Generación de semillas deterministas para funciones pseudoaleatorias (`rand()`).

### Límites de Responsabilidad y Delegación (Qué no cubre)
- Inyección de fallos dinámica en tiempo de ejecución vía `LD_PRELOAD` sin recompilar (delegado a `vasquez`).
- Ejecución aislada de casos de prueba con límites de CPU (delegado a `nostromo`).
- Generación de mutaciones de código fuente (delegado a `vassili`).

### Principios de Diseño
- **Enfoque Pedagógico:** Diagnósticos y mensajes en español rioplatense orientados a facilitar la comprensión de errores conceptuales.
- **Salida Estructurada Dual:** Soporte nativo para visualización enriquecida en terminal (Rich) y salida parseable para orquestadores (`--json`).
- **Integración Contractual:** Capacidad de emitir secciones de reporte para `dredd` (`dredd-section`) y actuar como satélite orquestado por `ripley`.
- **Idempotencia y Robustez:** Validación de precondiciones y comandos de autodiagnóstico (`doctor`) para verificación del entorno.

---

## 2. Instalación y Requisitos

### Requisitos del Sistema
- **Python:** `>= 3.10` (recomendado Python 3.11 o 3.12).
- **Gestor de paquetes:** [`uv`](https://github.com/astral-sh/uv) (entorno estándar de cátedra).
- **Toolchain C (si aplica):** GCC / Clang, Make, GDB y bibliotecas estándar de desarrollo.

### Instalación en el Entorno de Usuario
Para instalar la herramienta de forma global y aislada en el sistema mediante `uv tool`:
```bash
uv tool install --editable /home/mrtin/dev/tools/holden
```

### Verificación de Instalación
Ejecutá el comando `doctor` para constatar que todas las dependencias y binarios requeridos estén presentes y operativos:
```bash
holden doctor
```

---

## 3. Guía Integral de Comandos (CLI)

| Comando | Descripción Breve |
| :--- | :--- |
| [`holden generate`](#generate) | Genera un archivo C con la implementación del mock y wrapper de la función. |
| [`holden list`](#list) | Lista las funciones con soporte de mocks preconfigurados. |
| [`holden doctor`](#doctor) | Verifica el estado del entorno de HOLDEN (Python, GCC). |

### `holden generate`

Genera un archivo C con la implementación del mock y wrapper de la función.

#### Argumentos
| Argumento | Tipo | Descripción |
| :--- | :--- | :--- |
| `funcion` | `str` | Nombre de la función a mockear (ej: 'malloc', 'fopen', 'rand'). |

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--output`, `-o` | `Optional[Path]` | `None` | Archivo de destino donde escribir el código C del mock. |
| `--fail-at`, `-n` | `int` | `1` | Número de invocación en la que inyectar el fallo (retornar NULL). |
| `--json` | `bool` | `False` | Salida estructurada en JSON. |

#### Ejemplo de Invocación
```bash
holden generate <funcion>
```

### `holden list`

Lista las funciones con soporte de mocks preconfigurados.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json` | `bool` | `False` | Salida estructurada en JSON. |

#### Ejemplo de Invocación
```bash
holden list
```

### `holden doctor`

Verifica el estado del entorno de HOLDEN (Python, GCC).

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json` | `bool` | `False` | Emitir diagnóstico en formato JSON estructurado. |

#### Ejemplo de Invocación
```bash
holden doctor
```

---

## 4. Formatos de Salida e Integración con el Ecosistema

### Modo Interactivo / Terminal (Rich)
Por defecto, la herramienta renderiza paneles, árboles y tablas estilizadas para facilitar la lectura del estudiante y docente en terminales modernas con soporte ANSI.

### Modo Estructurado JSON (`--json`)
Para integración con pipelines de CI/CD, scripts de automatización u orquestadores externos, la opción `--json` emite un documento JSON estricto por la salida estándar (`stdout`), dirigiendo cualquier mensaje de logging a `stderr`:
```bash
holden generate --json
```

### Integración con Dredd (`dredd-section`)
Cuando la herramienta genera reportes de evaluación para entregas de alumnos, produce una sección Markdown estandarizada conforme al contrato de integración de Dredd (v1.0.0):
```markdown
<!-- dredd-section: holden, tool=holden, version=0.1.0, status=ok -->
```
Este encabezado garantiza la agregación determinista de los hallazgos en la rúbrica docente.

### Integración con Ripley
`holden` está registrada en el catálogo de plugins satélites de Ripley (`SATELLITE_CATALOG`). Puede invocarse directamente a través del motor de evaluación de Ripley configurando el análisis en `ripley.toml`.

---

## 5. Diagnóstico y Códigos de Salida

### Códigos de Retorno (`exit code`)
| Código | Significado |
| :---: | :--- |
| `0` | Ejecución exitosa sin hallazgos críticos ni errores de sintaxis. |
| `1` | Hallazgos pedagógicos detectados, infracción de reglas o advertencias activas. |
| `2` | Error de sintaxis en argumentos CLI o archivo fuente no encontrado. |
| `>2` | Error no recuperable del sistema, fallo de memoria o excepción interna. |

### Diagnóstico del Entorno (`doctor`)
Ante comportamientos inesperados, verificá el estado operativo con:
```bash
holden doctor
```
Comprueba la presencia de las dependencias requeridas y la integridad de los componentes del paquete.