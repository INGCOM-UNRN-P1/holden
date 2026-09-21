"""Tests de integración de la CLI de HOLDEN."""

import json
from pathlib import Path
from typer.testing import CliRunner
from holden.cli import app

runner = CliRunner()


def test_cli_version():
    res = runner.invoke(app, ["--version"])
    assert res.exit_code == 0
    assert "HOLDEN" in res.stdout


def test_cli_list():
    res = runner.invoke(app, ["list"])
    assert res.exit_code == 0
    assert "malloc" in res.stdout


def test_cli_generate_json():
    res = runner.invoke(app, ["generate", "malloc", "--fail-at", "3", "--json"])
    assert res.exit_code == 0
    data = json.loads(res.stdout)
    assert data["funcion"] == "malloc"
    assert "__wrap_malloc" in data["codigo_c"]


def test_cli_doctor():
    res = runner.invoke(app, ["doctor"])
    assert res.exit_code == 0
    assert "Diagnóstico del Entorno HOLDEN" in res.stdout

    res_json = runner.invoke(app, ["doctor", "--json"])
    assert res_json.exit_code == 0
    assert '"schema_version": "1.0.0"' in res_json.stdout
    assert '"herramienta": "holden"' in res_json.stdout
    assert '"ok": true' in res_json.stdout



def test_list_json():
    """HOLDEN-D0402: `list` ofrece --json con el inventario de funciones."""
    res = CliRunner().invoke(app, ["list", "--json"])
    assert res.exit_code == 0
    datos = json.loads(res.output)
    assert {f["funcion"] for f in datos["funciones"]} == {"malloc", "fopen", "rand"}
