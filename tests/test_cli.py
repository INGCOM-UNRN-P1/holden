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
