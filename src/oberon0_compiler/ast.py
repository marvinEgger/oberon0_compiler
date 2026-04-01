# SPDX-FileCopyrightText: 2026 Jacques Supcik <jacques.supcik@hefr.ch>
#
# SPDX-License-Identifier: Apache-2.0 OR MIT

"""
EBNF Abstract Syntax Tree
"""

from dataclasses import dataclass
from rich import print


@dataclass
class Node:
    def rich(self) -> str:
        return ""


@dataclass
class Factor(Node):
    pass



@dataclass
class Term(Node):
    factors: list[Factor]

    def rich(self) -> str:
        return " ".join(f"{f.rich()}" for f in self.factors)




@dataclass
class Identifier(Factor):
    value: str

    def rich(self) -> str:
        return f"[yellow]{self.value}[/yellow]"

@dataclass
class Literal(Factor):
    value: str

    def rich(self) -> str:
        return f"[green]'{self.value}'[/green]"

@dataclass
class Expression(Factor):
    terms: list[Term]
    paren: bool = False

    def rich(self) -> str:
        body = " | ".join(f"{t.rich()}" for t in self.terms)
        if self.paren:
            return f"[magenta]([/magenta] {body} [magenta])[/magenta]"
        return body


@dataclass
class Option(Factor):
    expr: Expression

    def rich(self) -> str:
        return f"[magenta][[/magenta] {self.expr.rich()} [magenta]][/magenta]"


@dataclass
class Repetition(Factor):
    expr: Expression

    def rich(self) -> str:
        return f"[magenta]{{[/magenta] {self.expr.rich()} [magenta]}}[/magenta]"


@dataclass
class Production(Node):
    identifier: Identifier
    expression: Expression

    def rich(self) -> str:
        return (
            f"[yellow]{self.identifier.rich()}[/yellow] [cyan]=[/cyan] "
            f"{self.expression.rich()}[cyan].[/cyan]"
        )


@dataclass
class Syntax(Node):
    production: list[Production]

    def rich(self) -> str:
        return "\n".join([p.rich() for p in self.production])