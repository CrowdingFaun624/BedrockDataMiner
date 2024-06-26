from typing import Any

from typing_extensions import Self

import Utilities.Exceptions as Exceptions
import Utilities.Nbt.Endianness as Endianness
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes

NoneType = type(None)

def stringify(data:Any) -> str:
    '''
    Returns the string of data containing no Diffs. Is used in the comparison reporter.
    :data: The data to stringify.
    '''
    match data:
        case NbtTypes.TAG():
            return str(data)
        case str():
            return "\"%s\"" % data
        case bool():
            return "true" if data else "false"
        case dict()|list()|int()|float()|bool():
            return str(data)
        case NoneType():
            return "null"
        case NbtReader.NbtBytes():
            try:
                return str(NbtReader.unpack_bytes(data.read(), gzipped=False, endianness=Endianness.End.BIG)[1])
            except Exception:
                try:
                    return str(NbtReader.unpack_bytes(data.read(), gzipped=False, endianness=Endianness.End.LITTLE)[1])
                except Exception:
                    return "Unencodable Nbt Object"
        case _:
            raise Exceptions.CannotStringifyError(type(data))

class Line():
    "A line of text in a comparison report."

    def __init__(self, text:str, *, indent:int=0) -> None:
        '''
        :text: The text to start this Line with.
        :indent: The number of indents this Line starts with.
        '''
        self.text = text
        self.indents = indent

    def set_indent(self, indents:int) -> None:
        '''
        Forcefully sets the indent of this line.
        :indents: The number of indents to set this Line to.
        '''
        self.indents = indents

    def indent(self, amount:int=1) -> Self:
        '''
        Increases the indent of this line.
        :amount: The amount to increase the indent by.
        '''
        self.indents += amount
        return self

    def __mod__(self, data:Any) -> Self:
        self.text %= data
        return self

    def __str__(self) -> str:
        return "\t" * self.indents + self.text

    def __repr__(self) -> str:
        return "<%s indent %i; len %i>" % (self.__class__.__name__, self.indents, len(self.text))
