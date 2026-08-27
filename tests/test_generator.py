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
