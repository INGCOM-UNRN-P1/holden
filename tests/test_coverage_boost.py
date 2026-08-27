"""Tests adicionales para maximizar la cobertura en HOLDEN."""

import json
from pathlib import Path
from typer.testing import CliRunner
import holden.cli
from holden.cli import app
from holden.core.generator import generar_mock
from holden.ripley_plugin import HoldenPlugin

runner = CliRunner()


def test_plugin_execution(tmp_path):
    p = HoldenPlugin()
    assert p.is_available() is True
    res = p.execute(tmp_path, {})
    assert res["ok"] is True
    assert (tmp_path / "holden_malloc_mock.c").is_file()


def test_cli_generate_file_and_rich(tmp_path):
    # Output to file
    out_file = tmp_path / "mock_fopen.c"
    res1 = runner.invoke(app, ["generate", "fopen", "-o", str(out_file), "-n", "2"])
    assert res1.exit_code == 0
    assert out_file.is_file()

    # Output to console rich panel
    res2 = runner.invoke(app, ["generate", "rand"])
    assert res2.exit_code == 0
    assert "__wrap_rand" in res2.stdout


def test_generar_mock_generico():
    mock = generar_mock("custom_fn")
    assert mock.funcion_objetivo == "custom_fn"
    assert "Mock genérico" in mock.codigo_c


def test_cli_main_block(monkeypatch):
    monkeypatch.setattr("sys.argv", ["holden", "--version"])
    try:
        holden.cli.main()
    except SystemExit as e:
        assert e.code == 0
