"""Tests unitarios para el generador de mocks en HOLDEN."""

from pathlib import Path
import pytest
from holden.core.generator import generar_mock


def test_generar_mock_malloc():
    mock = generar_mock("malloc", fail_at=2)
    assert mock.funcion_objetivo == "malloc"
    assert "__wrap_malloc" in mock.codigo_c
    assert "fail_at = 2" in mock.codigo_c


def test_generar_mock_rand():
    mock = generar_mock("rand", seed=1234)
    assert mock.funcion_objetivo == "rand"
    assert "__wrap_rand" in mock.codigo_c
    assert "1234" in mock.codigo_c


def test_funcion_no_soportada_sale_con_error_y_no_con_mock_vacio():
    """HOLDEN-D0301: `holden generate printf` daba exit 0 y un comentario."""
    from typer.testing import CliRunner
    from holden.cli import app

    res = CliRunner().invoke(app, ["generate", "printf"])
    assert res.exit_code == 2
    assert "printf" in res.output


def test_error_json_lista_las_funciones_soportadas():
    import json
    from typer.testing import CliRunner
    from holden.cli import app

    res = CliRunner().invoke(app, ["generate", "printf", "--json"])
    datos = json.loads(res.output)
    assert datos["ok"] is False
    assert set(datos["soportadas"]) == {"malloc", "fopen", "rand"}


def test_las_cabeceras_usan_el_prototipo_real():
    """Antes todas eran `void* __wrap_x();`, inválida para fopen (FILE*) y rand (int)."""
    assert "FILE* __wrap_fopen(const char* pathname, const char* mode);" in generar_mock("fopen").cabecera_c
    assert "int __wrap_rand(void);" in generar_mock("rand").cabecera_c
    assert "void* __wrap_malloc(size_t size);" in generar_mock("malloc").cabecera_c
