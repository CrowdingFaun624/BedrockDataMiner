from typing import Any

import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes
import Utilities.Nbt.Endianness as Endianness

NoneType = type(None)

def stringify(data:Any) -> str:
    '''Returns the string of data containing no Diffs. Is used in the comparison reporter.'''
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
                return str(NbtReader.unpack_bytes(data.open(), gzipped=False, endianness=Endianness.End.BIG)[1])
            except Exception:
                try:
                    return str(NbtReader.unpack_bytes(data.open(), gzipped=False, endianness=Endianness.End.LITTLE)[1])
                except Exception:
                    return "Unencodable Nbt Object"
        case _:
            try:
                stringified_data = str(data)
            except Exception: stringified_data = None
            if stringified_data is None:
                error_message = "Unencodable object of type \"%s\"!" % (data.__class__.__name__)
            else:
                error_message = "Unencodable object of type \"%s\": %s" % (data.__class__.__name__, stringified_data)
            raise TypeError(error_message)

class Line():

    def __init__(self, text:str, *, indent:int=0) -> None:
        self.text = text
        self.indents = indent

    def indent(self, amount:int=1) -> "Line":
        self.indents += amount
        return self
    
    def __mod__(self, data:Any) -> "Line":
        self.text %= data
        return self

    def __str__(self) -> str:
        return "\t" * self.indents + self.text
    
    def __repr__(self) -> str:
        return "<%s indent %i; len %i>" % (self.__class__.__name__, self.indents, len(self.text))
