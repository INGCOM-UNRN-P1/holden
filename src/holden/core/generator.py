"""Generador de código C para mocks y wrappers de inyección de fallos en HOLDEN."""

from __future__ import annotations

from typing import Dict, Optional
from holden.core.models import MockSpec

PLANTILLAS_MOCKS: Dict[str, str] = {
    "malloc": """// Mock para malloc() generado por HOLDEN
#include <stddef.h>
#include <stdlib.h>

static int __holden_malloc_calls = 0;
static int __holden_malloc_fail_at = {fail_at};

void* __real_malloc(size_t size);

void* __wrap_malloc(size_t size) {{
    __holden_malloc_calls++;
    if (__holden_malloc_fail_at > 0 && __holden_malloc_calls >= __holden_malloc_fail_at) {{
        return NULL; // Inyección de fallo de memoria
    }}
    return malloc(size);
}}
""",
    "fopen": """// Mock para fopen() generado por HOLDEN
#include <stdio.h>

static int __holden_fopen_calls = 0;
static int __holden_fopen_fail_at = {fail_at};

FILE* __wrap_fopen(const char* pathname, const char* mode) {{
    __holden_fopen_calls++;
    if (__holden_fopen_fail_at > 0 && __holden_fopen_calls >= __holden_fopen_fail_at) {{
        return NULL; // Inyección de fallo de apertura de archivo
    }}
    return fopen(pathname, mode);
}}
""",
    "rand": """// Mock para rand() determinista generado por HOLDEN
#include <stdlib.h>

static unsigned int __holden_seed = {seed};

int __wrap_rand(void) {{
    __holden_seed = __holden_seed * 1103515245 + 12345;
    return (unsigned int)(__holden_seed / 65536) % 32768;
}}
""",
}


def generar_mock(funcion: str, estrategia: str = "fail_after_n", **params) -> MockSpec:
    """Genera la especificación y código C del mock para la función solicitada."""
    fn = funcion.lower()
    fail_at = params.get("fail_at", 1)
    seed = params.get("seed", 42)

    plantilla = PLANTILLAS_MOCKS.get(fn)
    if not plantilla:
        codigo = f"// Mock genérico para {fn}\n"
    else:
        codigo = plantilla.format(fail_at=fail_at, seed=seed)

    cabecera = f"// Declaraciones para mock de {fn}\nvoid* __wrap_{fn}();\n"

    return MockSpec(
        funcion_objetivo=fn,
        estrategia=estrategia,
        parametros={"fail_at": fail_at, "seed": seed},
        cabecera_c=cabecera,
        codigo_c=codigo,
    )
