"""CLI de HOLDEN — Generador de mocks e inyección de fallos en C."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from holden import __version__
from holden.core.generator import PLANTILLAS_MOCKS, generar_mock

console = Console()
err_console = Console(stderr=True)

app = typer.Typer(
    name="holden",
    help="💉 HOLDEN — Generador de mocks e inyección controlada de fallos en funciones C (malloc, fopen, etc.).",
    add_completion=True,
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold cyan]HOLDEN[/bold cyan] versión [bold]{__version__}[/bold]")
        raise typer.Exit(code=0)


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Muestra la versión de HOLDEN.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    pass


@app.command("generate")
def generate_cmd(
    funcion: str = typer.Argument(..., help="Nombre de la función a mockear (ej: 'malloc', 'fopen', 'rand')."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Archivo de destino donde escribir el código C del mock."),
    fail_at: int = typer.Option(1, "--fail-at", "-n", help="Número de invocación en la que inyectar el fallo (retornar NULL)."),
    json_output: bool = typer.Option(False, "--json", help="Salida estructurada en JSON."),
) -> None:
    """Genera un archivo C con la implementación del mock y wrapper de la función."""
    mock = generar_mock(funcion, fail_at=fail_at)

    if output:
        output.write_text(mock.codigo_c, encoding="utf-8")

    if json_output:
        print(json.dumps(mock.to_dict(), indent=2, ensure_ascii=False))
        raise typer.Exit(code=0)

    if output:
        console.print(f"[green]✓ Mock generado exitosamente en {output}[/green]")
        console.print(f"[dim]Para compilar con GCC, agregá: '-Wl,--wrap={funcion}' y vinculá '{output.name}'[/dim]")
    else:
        console.print(Panel(
            Syntax(mock.codigo_c, "c", theme="monokai", line_numbers=True),
            title=f"Mock para {funcion}() (Falla en llamada #{fail_at})",
            border_style="cyan",
        ))


@app.command("list")
def list_cmd() -> None:
    """Lista las funciones con soporte de mocks preconfigurados."""
    tabla = Table(title="Funciones Disponibles para Mocks en HOLDEN")
    tabla.add_column("Función", style="bold cyan")
    tabla.add_column("Estrategia")
    tabla.add_column("Uso Pedagógico")

    tabla.add_row("malloc", "Fallo forzado NULL", "Verifica si el alumno chequea retornos de memoria")
    tabla.add_row("fopen", "Fallo forzado NULL", "Verifica chequeo de existencia de archivos")
    tabla.add_row("rand", "Semilla fija determinista", "Reproducibilidad exacta en tests de azar")

    console.print(tabla)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
