---
title: "Guía de Extensión y Uso Programático: holden"
subtitle: "Cómo se extiende holden, cómo lo consume ripley y cómo usarlo desde scripts y CI"
author: "Cátedra de Algoritmos y Programación"
date: "2026-08-31"
---

(manual-holden-plugins)=
# Guía de Extensión y Uso Programático: holden

````{abstract}
Esta guía explica cómo se extiende **`holden`** (agregando plantillas de mocks), cómo lo consume `ripley` como satélite, cómo usar su API Python desde un script y cómo integrarlo en una pipeline de CI/CD. Todo lo que aparece acá existe en el código: cada ejemplo está cubierto por un test de `tests/test_manual_plugins.py`.
````

---

(manual-holden-plugins-arquitectura)=
## 1. Arquitectura de Extensión

`holden` **no carga plugins de terceros**: no existe un grupo de entry points `holden.plugins` ni un comando `holden plugins`. Es un generador de código C con una tabla de plantillas, y se extiende agregando una entrada a esa tabla:

- **Plantillas**: `PLANTILLAS_MOCKS` en `src/holden/core/generator.py` asocia el nombre de una función (`malloc`, `fopen`, `rand`) con el código C del wrapper.
- **Cabeceras**: `CABECERAS_MOCKS` guarda el prototipo real de cada wrapper.
- **Formato de comunicación**: el dataclass `MockSpec` (`funcion`, `estrategia`, `parametros`, `cabecera_c`, `codigo_c`), que `to_dict()` convierte en JSON. No se usa Pydantic.

Lo que sí es un punto de extensión estándar es la **integración con ripley**: `holden` se registra como satélite en el grupo `ripley.plugins` de su `pyproject.toml`:

````{code-block} toml
[project.entry-points."ripley.plugins"]
mocks = "holden.ripley_plugin:HoldenPlugin"
````

`HoldenPlugin.execute(workspace, manifest_config)` genera un mock de `malloc` en el workspace y devuelve el archivo y las banderas de enlace (`-Wl,--wrap=malloc`) que ripley necesita para compilar con la inyección de fallos.

---

(manual-holden-plugins-tutorial)=
## 2. Agregar el Mock de una Función Nueva

Como ejemplo agregamos `calloc`, que falla a partir de la N-ésima invocación igual que `malloc`.

### Paso 1: Escribir la plantilla

En `PLANTILLAS_MOCKS` el código C se formatea con `str.format`, así que las llaves del C van **duplicadas** (`{{` y `}}`) y los únicos campos son `{fail_at}` y `{seed}`:

````{code-block} python
:linenos:
PLANTILLAS_MOCKS["calloc"] = """// Mock para calloc() generado por HOLDEN
#include <stddef.h>
#include <stdlib.h>

static int __holden_calloc_calls = 0;
static int __holden_calloc_fail_at = {fail_at};

void* __real_calloc(size_t n, size_t size);

void* __wrap_calloc(size_t n, size_t size) {{
    __holden_calloc_calls++;
    if (__holden_calloc_fail_at > 0 && __holden_calloc_calls >= __holden_calloc_fail_at) {{
        return NULL;
    }}
    return __real_calloc(n, size);
}}
"""
````

### Paso 2: Declarar los prototipos

Sin esta entrada `generar_mock("calloc")` falla con `KeyError` al armar la cabecera:

````{code-block} python
CABECERAS_MOCKS["calloc"] = (
    "void* __wrap_calloc(size_t n, size_t size);\n"
    "void* __real_calloc(size_t n, size_t size);\n"
)
````

### Paso 3: Verificar

````{code-block} bash
holden list
holden generate calloc --fail-at 3 -o mock_calloc.c
````

---

(manual-holden-plugins-sdk)=
## 3. Conexión Programática mediante la API Python

Podés generar mocks desde un script sin invocar subprocesos:

````{code-block} python
:linenos:
from holden.core.generator import FuncionNoSoportada, generar_mock

try:
    mock = generar_mock("malloc", fail_at=3)
except FuncionNoSoportada as error:
    print(error)          # p. ej. pedir "printf"
else:
    print(mock.funcion_objetivo)   # "malloc"
    print(mock.parametros)         # {"fail_at": 3, "seed": 42}
    open("mock_malloc.c", "w").write(mock.codigo_c)
````

`generar_mock` **falla con `FuncionNoSoportada`** ante una función sin plantilla: no inventa un mock vacío.

---

(manual-holden-plugins-ci)=
## 4. Integración en Pipelines de CI/CD (GitHub Actions / GitLab CI)

Un mock sirve en CI para comprobar que un programa **maneja el fallo de una asignación o de una apertura de archivo**. `holden` genera el wrapper y el enlazador lo inserta con `--wrap`:

````{code-block} yaml
# .github/workflows/robustez.yml
name: Robustez ante fallos de memoria
on: [push, pull_request]

jobs:
  mocks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Instalar holden
        run: pip install ./holden

      - name: Generar el mock (falla desde la primera llamada)
        run: holden generate malloc --fail-at 1 -o mock_malloc.c

      - name: Compilar enlazando el wrapper
        run: gcc -Wall -Wextra src/main.c mock_malloc.c -Wl,--wrap=malloc -o main_mock

      - name: El programa debe terminar con un error controlado, no con una señal
        run: ./main_mock || test $? -lt 128
````

---

(manual-holden-plugins-ejercicios)=
## 5. Ejercicios de Extensión Práctica

````{exercise} Ejercicio 1: Un mock para calloc
Agregá `calloc` siguiendo la sección 2 y comprobá con `holden generate calloc --fail-at 2` que el código generado compila.

**Pasos sugeridos:**
1. Agregar la plantilla a `PLANTILLAS_MOCKS` duplicando las llaves del C.
2. Agregar los prototipos a `CABECERAS_MOCKS`.
3. Escribir un test que llame a `generar_mock("calloc", fail_at=2)`.
````

````{solution} Ejercicio 1
```python
from holden.core.generator import generar_mock

def test_calloc():
    mock = generar_mock("calloc", fail_at=2)
    assert "__wrap_calloc" in mock.codigo_c
    assert "__holden_calloc_fail_at = 2" in mock.codigo_c
```
````

````{exercise} Ejercicio 2: Qué significa fail-at
Compilá un programa que llame tres veces a `malloc` con `--fail-at 2` y contá cuántas llamadas devuelven `NULL`.

**Pista:** el wrapper falla cuando el contador **alcanza o supera** `fail_at`.
````

````{solution} Ejercicio 2
Devuelven `NULL` la segunda y la tercera llamada (dos de tres): el mock falla *a partir de* la N-ésima invocación, no solo en ella.
````
