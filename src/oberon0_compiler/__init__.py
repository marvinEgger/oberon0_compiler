# SPDX-FileCopyrightText: 2026 Jacques Supcik <jacques.supcik@hefr.ch>
#
# SPDX-License-Identifier: MIT

"""
Oberon-0 compiler
"""

import sys
from pathlib import Path
from typing import Annotated, TypeAlias

import typer
from loguru import logger
from rich.console import Console

from .scanner import Scanner

console = Console()
app = typer.Typer()


FilterDict: TypeAlias = dict[str | None, str | int | bool]


__version__ = "0.1.2"


def version_callback(value: bool) -> None:
    if value:
        print(f"Oberon0 compiler version: {__version__}")
        raise typer.Exit()


@app.command(context_settings={"ignore_unknown_options": False})
def main(  # noqa: PLR0913
    source: Annotated[Path, typer.Argument(help="Oberon-0 source file (.mod)")],
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = None,
    debug: bool = False,
    debug_scanner: bool = False,
) -> None:
    "Oberon-0 compiler"

    logger.remove()

    level_per_module: FilterDict = {"": "INFO"}

    if debug:
        level_per_module[""] = "DEBUG"
    if debug_scanner:
        level_per_module["oberon0_compiler.scanner"] = "DEBUG"

    logger.add(sys.stdout, filter=level_per_module, level=0)

    scanner = Scanner()
    try:
        source_file = source.open("r")
        scanner.open(source_file)
    except OSError as e:
        logger.error(f"Cannot open source file {source}: {e}")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()