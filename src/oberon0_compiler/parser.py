# SPDX-FileCopyrightText: 2026 Jacques Supcik <jacques.supcik@hefr.ch>
#
# SPDX-License-Identifier: Apache-2.0 OR MIT

"""
EBNF Parser
"""

from dataclasses import dataclass

from loguru import logger

from .scanner import Scanner
from .tokens import Token

from . import ast

@dataclass
class Parser:
    scanner: Scanner
    has_error: bool = False

    def raise_error(self, msg: str) -> None:
        self.has_error = True
        self.scanner.print_error(msg)
        raise Exception(msg)

    def raise_expected_error(self, expected: Token):
        self.raise_error(f"Expected '{expected}', but got '{self.scanner.sym}'")

    def factor(self) -> ast.Factor:
        logger.debug("Factor")
        sym = self.scanner.sym
        node: ast.Factor
        if sym == Token.IDENT:
            node = ast.Identifier(value=self.scanner.value)
            self.scanner.get_next_symbol()
            return node
        elif sym == Token.LITERAL:
            node = ast.Literal(value=self.scanner.value)
            self.scanner.get_next_symbol()
            return node
        elif sym == Token.LPAREN:
            self.scanner.get_next_symbol()
            node =self.expression()
            node.paren = True
            if self.scanner.sym != Token.RPAREN:
                self.raise_expected_error(Token.RPAREN)
            self.scanner.get_next_symbol()
            return node
        elif sym == Token.LBRAK:
            self.scanner.get_next_symbol()
            node = self.expression()
            if self.scanner.sym != Token.RBRAK:
                self.raise_expected_error(Token.RBRAK)
            self.scanner.get_next_symbol()
            return ast.Option(expr=node)
        elif sym == Token.LBRACE:
            self.scanner.get_next_symbol()
            node = self.expression()
            if self.scanner.sym != Token.RBRACE:
                self.raise_expected_error(Token.RBRACE)
            self.scanner.get_next_symbol()
            return ast.Repetition(expr=node)
        else:
            self.raise_error(
                f"Expected identifier, literal, (', '['. or '{{' got {sym}"
            )
            raise Exception("Unexpected symbol")

    def term(self) -> ast.Term:
        logger.debug("Term")
        node: ast.Term = ast.Term(factors=[])
        factor: ast.Factor | None = self.factor()

        node.factors.append(factor)
        while self.scanner.sym in (
            Token.IDENT,
            Token.LITERAL,
            Token.LPAREN,
            Token.LBRAK,
            Token.LBRACE,
        ):
            factor = self.factor()
            node.factors.append(factor)
        return node

    def expression(self) -> ast.Expression:
        logger.debug("Expression")
        node: ast.Expression = ast.Expression(terms=[])
        node.terms.append(self.term())
        while self.scanner.sym == Token.BAR:
            self.scanner.get_next_symbol()
            node.terms.append(self.term())
        return node
    def production(self) -> ast.Production:
        logger.debug("Production")
        ident = ast.Identifier(value=self.scanner.value)
        
        self.scanner.get_next_symbol()
        if self.scanner.sym != Token.EQL:
            self.raise_expected_error(Token.EQL)
        self.scanner.get_next_symbol()
        expr: ast.Expression = self.expression()
        if self.scanner.sym != Token.PERIOD:
            self.raise_expected_error(Token.PERIOD)
        self.scanner.get_next_symbol()
        return ast.Production(identifier=ident, expression=expr)
         
    def syntax(self) -> ast.Syntax:
        logger.debug("Syntax")
        node: ast.Syntax = ast.Syntax(production=[])
        while self.scanner.sym != Token.EOF:
            if self.scanner.sym != Token.IDENT:
                self.raise_expected_error(Token.IDENT)
            node.production.append(self.production())
        return node

    def parse(self) -> ast.Syntax | None:
        logger.debug("Parsing")
        self.scanner.get_next_symbol()
        return self.syntax()
