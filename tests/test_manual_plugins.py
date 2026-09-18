"""Regresión de HOLDEN-D0801: el manual describía una arquitectura de extensión inexistente.

Documentaba el grupo de entry points `holden.plugins`, `holden plugins list`, la API
`holden.ejecutar_analisis` y modelos Pydantic; nada de eso existe. Estos tests ejecutan
lo que el manual ahora afirma.
"""

import re
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

from holden.core import generator
from holden.core.generator import FuncionNoSoportada, generar_mock

RAIZ = Path(__file__).resolve().parents[1]
MANUAL = (RAIZ / "manual" / "plugins.md").read_text(encoding="utf-8")
necesita_gcc = pytest.mark.skipif(not shutil.which("gcc"), reason="requiere gcc")


def _bloques_python():
    return re.findall(r"````\{code-block\} python\n(?::linenos:\n)?(.*?)````", MANUAL, re.S)


def test_el_manual_no_documenta_lo_que_no_existe():
    for fantasma in ("holden.plugins", "holden plugins list", "ejecutar_analisis", "resultado.items"):
        assert fantasma not in MANUAL.replace('no existe un grupo de entry points `holden.plugins`', "").replace(
            "ni un comando `holden plugins`", ""
        ), fantasma


def test_el_entry_point_documentado_es_el_declarado():
    datos = tomllib.loads((RAIZ / "pyproject.toml").read_text(encoding="utf-8"))
    assert datos["project"]["entry-points"]["ripley.plugins"]["mocks"] == "holden.ripley_plugin:HoldenPlugin"
    assert "holden.ripley_plugin:HoldenPlugin" in MANUAL
    assert "holden.plugins" not in datos["project"].get("entry-points", {})


def test_una_funcion_sin_plantilla_falla_en_vez_de_inventar_un_mock():
    with pytest.raises(FuncionNoSoportada):
        generar_mock("printf")


def test_el_mockspec_tiene_los_campos_que_el_manual_lista():
    campos = set(generar_mock("malloc").to_dict())
    assert campos == {"funcion", "estrategia", "parametros", "cabecera_c", "codigo_c"}


@pytest.fixture
def calloc_del_manual(monkeypatch):
    """Ejecuta los bloques del manual que agregan `calloc` y devuelve la plantilla resultante."""
    espacio = {"PLANTILLAS_MOCKS": {}, "CABECERAS_MOCKS": {}}
    for bloque in _bloques_python():
        if "PLANTILLAS_MOCKS[" in bloque or "CABECERAS_MOCKS[" in bloque:
            exec(bloque, espacio)
    monkeypatch.setitem(generator.PLANTILLAS_MOCKS, "calloc", espacio["PLANTILLAS_MOCKS"]["calloc"])
    monkeypatch.setitem(generator.CABECERAS_MOCKS, "calloc", espacio["CABECERAS_MOCKS"]["calloc"])


def test_el_calloc_del_manual_se_genera(calloc_del_manual):
    mock = generar_mock("calloc", fail_at=2)
    assert "__wrap_calloc" in mock.codigo_c
    assert "__holden_calloc_fail_at = 2" in mock.codigo_c


@necesita_gcc
def test_el_calloc_del_manual_compila_y_falla_a_partir_de_la_llamada_n(calloc_del_manual, tmp_path):
    (tmp_path / "mock.c").write_text(generar_mock("calloc", fail_at=2).codigo_c, encoding="utf-8")
    (tmp_path / "p.c").write_text(
        "#include <stdio.h>\n#include <stdlib.h>\n"
        'int main(void) { int nulos = 0; for (int i = 0; i < 3; i++) { void *p = calloc(1, 8); if (!p) nulos++; }\n'
        '  printf("%d\\n", nulos); return 0; }\n',
        encoding="utf-8",
    )
    subprocess.run(
        ["gcc", str(tmp_path / "p.c"), str(tmp_path / "mock.c"), "-Wl,--wrap=calloc", "-o", str(tmp_path / "p")],
        check=True,
    )
    salida = subprocess.run([str(tmp_path / "p")], capture_output=True, text=True, check=True).stdout
    assert salida.strip() == "2", "el mock falla a partir de la 2.ª llamada: la 2.ª y la 3.ª (ejercicio 2)"


@necesita_gcc
def test_el_flujo_de_ci_documentado_funciona(tmp_path):
    mock = tmp_path / "mock_malloc.c"
    from typer.testing import CliRunner
    from holden.cli import app

    res = CliRunner().invoke(app, ["generate", "malloc", "--fail-at", "1", "-o", str(mock)])
    assert res.exit_code == 0, res.output

    (tmp_path / "main.c").write_text(
        "#include <stdlib.h>\n#include <stdio.h>\n"
        'int main(void) { int *v = malloc(4 * sizeof *v); if (!v) { fprintf(stderr, "sin memoria\\n"); return 1; } free(v); return 0; }\n',
        encoding="utf-8",
    )
    subprocess.run(
        ["gcc", "-Wall", "-Wextra", str(tmp_path / "main.c"), str(mock), "-Wl,--wrap=malloc", "-o", str(tmp_path / "main_mock")],
        check=True,
    )
    codigo = subprocess.run([str(tmp_path / "main_mock")], capture_output=True).returncode
    assert 0 < codigo < 128, "un manejo correcto del fallo termina con un error controlado, no con una señal"
