# SPDX-FileCopyrightText: 2026 Jacques Supcik <jacques.supcik@hefr.ch>
#
# SPDX-License-Identifier: MIT

"""
Oberon-0 scanner
"""

import io
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .token import Token


@dataclass
class Position:
    file_name: str
    line_no: int
    col_no: int


class ScannerError(Exception):
    def __init__(self, message: str, position: Position) -> None:
        super().__init__(message)
        self.position = position

    def __str__(self) -> str:
        p = self.position
        return (
            f"{self.args[0]} (File {p.file_name}, Line {p.line_no}, Column {p.col_no})"
        )


# @typing.no_type_check
@dataclass
class Scanner:
    eof: bool = False
    sym: Enum | None = None  # Next Symbol
    value: str = ""
    file_name: Path | None = None
    line_no: int = 0
    col_no: int = 0

    _ch: str = ""
    _text: io.TextIOBase | None = None
    _text_line: str = ""

    _keyword = {str(i): i for i in Token if str(i).isupper()}
    _symbol = {
        str(i): i for i in Token if not str(i).isupper() and not str(i).islower()
    }

    def open(self, text: io.TextIOBase) -> None:
        self._text = text
        if isinstance(text, io.TextIOWrapper):
            self.file_name = Path(text.name)
        else:
            self.file_name = None

        self.get_next_char()

    def position(self) -> Position:
        return Position(
            file_name=str(self.file_name) if self.file_name else "",
            line_no=self.line_no,
            col_no=self.col_no,
        )

    def skip_space(self) -> None:
        while self._ch.isspace():
            self.get_next_char()

    def skip_comment(self) -> None:
        while True:
            self.get_next_char()
            if self.eof:
                raise ScannerError("Unterminated comment", self.position())
            if self._ch == "(":
                self.get_next_char()
                if self._ch == "*":
                    self.get_next_char()
                    self.skip_comment()
            if self._ch == "*":
                self.get_next_char()
                if self._ch == ")":
                    self.get_next_char()
                    return

    def get_next_char(self) -> None:
        assert self._text is not None
        while not self.eof and self._text_line == "":
            self._text_line = self._text.readline()
            self.line_no += 1
            self.col_no = 0
            if self._text_line == "":
                self.eof = True
                break
            self._text_line = self._text_line.rstrip()
        if self.eof:
            self._ch = ""
        else:
            assert self._text_line != ""
            self._ch = self._text_line[0]
            self._text_line = self._text_line[1:]
            self.col_no += 1

    def get_next_symbol(self) -> None:  # noqa: C901
        """This method should set the following attributes:
        - `self.sym` to the next symbol (of type `Token`)
        - `self.value` to the value of the symbol (if applicable, e.g. for identifiers and numbers)
        - `self.eof` to `True` if the end of file is reached, `False` otherwise
        """
        # TODO(Student) : Implémentez la méthode `get_next_symbol`

        self.skip_space()
        self.value = ""

        if self.eof:
            self.sym = Token.EOF
            self.value = ""
            return

        # handle numbers
        if self._ch.isnumeric():

            while self._ch.isnumeric():
                # set the value to the value of the next symbol
                self.value += self._ch
                self.get_next_char()

            self.sym = Token.NUMBER
            return
        
         # handle alpha num, all token that are not symbols and numbers are identifiers or keywords, we need to check if they are keywords or identifiers
        if self._ch.isalpha():
            while self._ch.isalnum():
                # set the value to the value of the next symbol
                self.value += self._ch
                self.get_next_char()

                # if value is a valid token, keep as candidate (> ad candidate, not sure if <=)
              
            if self.value in self._keyword:
                    self.sym = self._keyword[self.value]
            else:
                self.sym = Token.IDENT
            return
        
        # handle symbols
        self.value += self._ch  
        self.get_next_char()

        while self._ch != "" and (self.value + self._ch) in self._symbol:
            self.value += self._ch
            self.get_next_char()

        if self.value in self._symbol:
            self.sym = self._symbol[self.value]
        else:
            raise ScannerError(f"Unknown symbol: '{self.value}'", self.position())
        return


