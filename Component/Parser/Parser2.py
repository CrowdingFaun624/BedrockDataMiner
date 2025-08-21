from itertools import count
from pathlib import Path
from typing import Callable, Container, Final, Literal, Sequence

import Domain.Domain as Domain
from Component.Field.ComponentField import ComponentField
from Component.Field.ComponentTypeField import ComponentTypeField
from Component.Field.ConcatenationField import ConcatenationField
from Component.Field.CTypeField import CTypeField
from Component.Field.DictField import DictField
from Component.Field.DomainField import DomainField
from Component.Field.Errors import Errors
from Component.Field.FieldFactory import FieldFactory
from Component.Field.GroupField import GroupField
from Component.Field.ListField import ListField
from Component.Field.PrimitiveField import PrimitiveField
from Component.Field.ReferenceField import ReferenceField
from Component.Field.ScriptField import ScriptField
from Component.Field.TypeField import TypeField
from Component.Field.Variable import Variable
from Component.Field.VariableReferenceField import VariableReferenceField
from Component.Group import Aliases, Group, GroupSettings
from Component.Parser.Lexer import SettingsToken, Token, lex
from Component.Parser.Reader import Reader
from Component.Scope import Scope


class TokenReader():
    """
    An object that provides a neat API for interacting with the Token sequence.

    :param tokens: The sequence of Tokens.
    """

    __slots__ = (
        "index",
        "tokens",
    )

    def __init__(self, tokens:Sequence[Token]) -> None:
        self.tokens:Final = tokens
        self.index:int = 0

    def read(self, offset:int, /, move_to:bool=False) -> Token|None:
        """
        Reads a single Token.

        :param offset: How far from the current offset to read a Token from.
        :param move_to: If True, the index will be moved to the position read from.
        :returns: A Token, or None if it is out of bounds.
        """
        position = self.index + offset
        if position < 0 or position >= len(self.tokens):
            return None
        if move_to:
            self.index = position
        return self.tokens[position]

    def move(self, offset:int) -> bool:
        """
        Moves the index.

        :offset: The amount to change the index by.
        :returns: If the new position is out-of-bounds.
        """
        self.index += offset
        return self.index < 0 or self.index >= len(self.tokens)

def parse_file(string_reader:Reader, /, domain:"Domain.Domain", path:Path) -> Group:
    error = Errors.fine
    tokens, new_error = lex(string_reader)
    error = error.narrow(new_error)
    reader = TokenReader(tokens)

    settings:GroupSettings|None = None
    fields:dict[str,FieldFactory] = {}
    fields:dict[str,FieldFactory] = {}
    while not reader.move(0):
        if isinstance(reader.read(0), SettingsToken):
            fields, variables, new_error = parse_fields(reader)
            error = error.narrow(new_error)
            if len(variables) > 0:
                reader.exception()
