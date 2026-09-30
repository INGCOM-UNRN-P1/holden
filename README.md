# 💉 HOLDEN — Generador de Mocks e Inyección de Fallos en C

> 📖 **Manual de Usuario:** Para una guía exhaustiva de comandos, banderas, arquitectura y ejemplos, consultá el [Manual de Uso](MANUAL.md).

HOLDEN permite generar mocks y envoltorios de enlace (`-Wl,--wrap=symbol`) para simular condiciones adversas de ejecución en pruebas de software C (fallos de `malloc()`, errores de apertura en `fopen()`, generación pseudoaleatoria determinista).

---

## 🎯 Alcance

### Qué cubre
- Generación de arneses de prueba unitaria en C con aislamiento de dependencias externas.
- Síntesis de funciones de sustitución (Mocks y Stubs) a nivel de código fuente y de enlazador GNU (`ld --wrap`).
- Inyección determinista y programable de fallos de biblioteca: `malloc` retornando `NULL`, `fopen` fallando con error de archivo inexistente (`ENOENT`), o simulación de lecturas truncadas.
- Generación de semillas deterministas para funciones pseudoaleatorias (`rand()`).

### Qué no cubre (Límites y Delegación)
- Inyección de fallos dinámica en tiempo de ejecución vía `LD_PRELOAD` sin recompilar (delegado a `vasquez`).
- Ejecución aislada de casos de prueba con límites de CPU (delegado a `nostromo`).
- Generación de mutaciones de código fuente (delegado a `vassili`).

---

## 📋 Requisitos

### Requisitos de Sistema y Entorno
- Linux / POSIX o Windows (MSYS2 / WSL). Python >= 3.10.

### Dependencias Externas y Binarios
- `gcc`, `ld`.

### Integración en el Ecosistema
- CLI `holden`. Plugin registrado en `ripley.plugins` (`mocks`).

---

## Uso Rápido

```bash
# 1. Generar mock de malloc que falla en la 2da llamada
holden generate malloc --fail-at 2 -o mock_malloc.c

# 2. Salida estructurada JSON
holden generate malloc --json

# 3. Listar funciones mockeables soportadas
holden list
```

<!-- p1:referencia:inicio — generado por p1-tools/scripts/readme_generado.py: no editar a mano -->

## Referencia rápida

### Requisitos

- Python ≥ 3.11 y [uv](https://docs.astral.sh/uv/getting-started/installation/).
- Programas del sistema: `gcc`.

| Sistema | `gcc` |
|:--|:--|
| Debian / Ubuntu | `sudo apt install gcc` |
| Fedora | `sudo dnf install gcc` |
| Windows | incluido en el entorno de la cátedra (MSYS2 UCRT64) |
| macOS | `xcode-select --install` (clang como `gcc`) |

### Comandos

| Comando | Descripción |
|:--|:--|
| `holden generate` | Genera un archivo C con la implementación del mock y wrapper de la función. |
| `holden list` | Lista las funciones con soporte de mocks preconfigurados. |
| `holden doctor` | Verifica el estado del entorno de HOLDEN (Python, GCC). |

Ayuda de cada comando: `holden <comando> -h`.

<!-- p1:referencia:fin -->
