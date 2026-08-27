"""Plugin de HOLDEN para integración transparente con RIPLEY."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from holden.core.generator import generar_mock


class HoldenPlugin:
    """Plugin de generación de mocks e inyección de fallos para Ripley."""

    name = "mocks"
    version = "0.1.0"

    def is_available(self) -> bool:
        return True

    def execute(self, workspace: Path, manifest_config: Dict[str, Any]) -> Dict[str, Any]:
        mock_malloc = generar_mock("malloc", fail_at=1)
        mock_file = workspace / "holden_malloc_mock.c"
        mock_file.write_text(mock_malloc.codigo_c, encoding="utf-8")

        return {
            "ok": True,
            "mocks_generados": ["malloc"],
            "archivo_mock": str(mock_file),
            "ldflags": ["-Wl,--wrap=malloc"],
        }
