from typing import Optional

import _domains.minecraft_common.scripts.Nbt.SnbtParser as SnbtParser
import Utilities.Exceptions as Exceptions


class NbtException(Exception):
    "Abstract Exception class for errors relating to NBT."

class NbtParseException(NbtException):
    "Abstract Exception class for errors relating to the parsing of NBT from bytes."

class CompoundDuplicateKeyError(NbtParseException):
    "A TAG_Compound has a duplicate key."

    def __init__(self, key:str, message:Optional[str]=None) -> None:
        '''
        :key: The key that was duplicated.
        :message: Additional text to place after the main message.
        '''
        super().__init__(key, message)
        self.key = key
        self.message = message

    def __str__(self) -> str:
        return f"A TAG_Compound has a duplicate key \"{self.key}\"{Exceptions.message(self.message)}"

class InvalidNbtContentType(NbtParseException):
    "An NBT tag has an invalid content type."

    def __init__(self, content_type:int, message:Optional[str]=None) -> None:
        '''
        :content_type: The content type ID.
        :message: Additional text to place after the main message.
        '''
        super().__init__(content_type, message)
        self.content_type = content_type
        self.message = message

    def __str__(self) -> str:
        return f"Invalid NBT content type {self.content_type}{Exceptions.message(self.message)}"

class NbtTestFailureError(NbtException):
    "An NBT test has failed."

class SnbtParseError(NbtException):
    def __init__(self, message:str, reader:"SnbtParser.Reader", other_exceptions:list["SnbtParseError"]|None=None) -> None:
        super().__init__(message, reader.position, reader.stack, other_exceptions)
