"""Modelos de datos para el generador de mocks en HOLDEN."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class MockSpec:
    """Especificación de un mock para inyectar en compilación o enlace."""
    funcion_objetivo: str       # "malloc", "fopen", "rand", "time"
    # Etiqueta informativa: el comportamiento real lo fijan `parametros`
    # (`fail_at` para malloc/fopen: falla desde la N-ésima llamada; `seed` para rand).
    estrategia: str
    parametros: Dict[str, Any] = field(default_factory=dict)
    cabecera_c: str = ""
    codigo_c: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "funcion": self.funcion_objetivo,
            "estrategia": self.estrategia,
            "parametros": self.parametros,
            "cabecera_c": self.cabecera_c,
            "codigo_c": self.codigo_c,
        }
