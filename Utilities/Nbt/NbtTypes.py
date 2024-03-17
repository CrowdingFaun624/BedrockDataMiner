import enum
import mutf8
import re
from typing import Generic, TypeVar

import Utilities.Nbt.DataReader as DataReader
import Utilities.Nbt.Endianness as Endianness

class IdEnum(enum.IntEnum):
    TAG_End = 0
    TAG_Byte = 1
    TAG_Short = 2
    TAG_Int = 3
    TAG_Long = 4
    TAG_Float = 5
    TAG_Double = 6
    TAG_Byte_Array = 7
    TAG_String = 8
    TAG_List = 9
    TAG_Compound = 10
    TAG_Int_Array = 11
    TAG_Long_Array = 12

a = TypeVar("a")

class TAG(Generic[a]):

    value:a

    def __init__(self, value:a) -> None:
        self.value = value

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG": ...

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, self.__class__) and self.value == __value.value

    def __str__(self) -> str: ...

class TAG_End(TAG[None]):

    value = None

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_End":
        return cls(None)

    def __str__(self) -> str:
        return "<END>"

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, TAG_End)

class TAG_Byte(TAG[int]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_Byte":
        return cls(data_reader.unpack_tuple("b", 1, None))

    def __str__(self) -> str:
        return "%ib" % self.value

class TAG_Short(TAG[int]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_Short":
        return cls(data_reader.unpack_tuple("h", 2, endianness.short_char))

    def __str__(self) -> str:
        return "%is" % self.value

class TAG_Int(TAG[int]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_Int":
        return cls(data_reader.unpack_tuple("i", 4, endianness.int_char))

    def __str__(self) -> str:
        return "%i" % self.value

class TAG_Long(TAG[int]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_Long":
        return cls(data_reader.unpack_tuple("q", 8, endianness.long_char))

    def __str__(self) -> str:
        return "%il" % self.value

class TAG_Float(TAG[float]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_Float":
        return cls(data_reader.unpack_tuple("f", 4, endianness.float_char))

    def __str__(self) -> str:
        return "%ff" % self.value

class TAG_Double(TAG[float]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_Double":
        return cls(data_reader.unpack_tuple("d", 8, endianness.double_char))

    def __str__(self) -> str:
        return "%f" % self.value

class TAG_Byte_Array(TAG[list[TAG_Byte]]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_Byte_Array":
        size:int = data_reader.unpack_tuple("i", 4, endianness.int_char)
        return cls([TAG_Byte.from_bytes(data_reader, endianness) for i in range(size)])

    def __str__(self) -> str:
        return "[B;" + ", ".join(str(item) for item in self.value) + "]"

class TAG_String(TAG[str]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_String":
        size:int = data_reader.unpack_tuple("H", 2, endianness.short_char)
        output2:tuple[bytes] = data_reader.unpack("c" * size, size, None)
        return cls(mutf8.decode_modified_utf8(b"".join(output2)))

    def __str__(self) -> str:
        return "\"%s\"" % escape_string(self.value)

class TAG_List(TAG[list[TAG]]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_List":
        content_type:int = data_reader.unpack_tuple("b", 1, None)
        size:int = data_reader.unpack_tuple("i", 4, endianness.int_char)
        return cls([parse_object_from_bytes(data_reader, content_type, endianness) for i in range(size)])

    def __str__(self) -> str:
        return "[" + ", ".join(str(item) for item in self.value) + "]"

class TAG_Compound(TAG[dict[str,TAG]]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_Compound":
        output:dict[str,TAG] = {}
        while True:
            key_name, value = parse_compound_item_from_bytes(data_reader, endianness)
            if isinstance(value, TAG_End):
                break
            if key_name in output:
                raise KeyError("Duplicate key \"%s\"!" % key_name)
            assert key_name is not None
            output[key_name] = value
        return cls(output)

    def __str__(self) -> str:
        output = "{"
        for index, (key, value) in enumerate(self.value.items()):
            if self.should_enquote_key(key):
                output += "\"%s\"" % escape_string(key)
            else:
                output += key
            output += ": "
            output += str(value)
            if index != len(self.value) - 1:
                output += ", "
        output += "}"
        return output

    def should_enquote_key(self, key:str, pattern=re.compile(r'[^a-zA-Z0-9.]').search) -> bool:
        if len(key) == 0: return True
        return bool(pattern(key))

class TAG_Int_Array(TAG[list[TAG_Int]]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_Int_Array":
        size:int = data_reader.unpack_tuple("i", 4, endianness.int_char)
        return cls([TAG_Int.from_bytes(data_reader, endianness) for i in range(size)])

    def __str__(self) -> str:
        return "[I;" + ", ".join(str(item) for item in self.value) + "]"

class TAG_Long_Array(TAG[list[TAG_Long]]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> "TAG_Long_Array":
        size:int = data_reader.unpack_tuple("i", 4, endianness.int_char)
        return cls([TAG_Long.from_bytes(data_reader, endianness) for i in range(size)])

    def __str__(self) -> str:
        return "[L;" + ", ".join(str(item) for item in self.value) + "]"

def escape_string(string:str) -> str:
    output = ""
    for char in string:
        match char:
            case "\"": output += "\\\""
            case "\\": output += "\\\\"
            case _: output += char
    return output

def parse_compound_item_from_bytes(data_reader:DataReader.DataReader, endianness:Endianness.Endianness) -> tuple[str|None,TAG]:
    content_type:int = data_reader.unpack_tuple("b", 1, None)
    if content_type == IdEnum.TAG_End:
        return None, TAG_End.from_bytes(data_reader, endianness) # TAG_End has no name
    key_name:str = parse_object_from_bytes(data_reader, IdEnum.TAG_String, endianness).value
    value = parse_object_from_bytes(data_reader, content_type, endianness)
    return key_name, value

def parse_object_from_bytes(data_reader:DataReader.DataReader, content_type:int, endianness:Endianness.Endianness) -> TAG:
    match content_type:
        case IdEnum.TAG_End:        return TAG_End.from_bytes(data_reader, endianness)
        case IdEnum.TAG_Byte:       return TAG_Byte.from_bytes(data_reader, endianness)
        case IdEnum.TAG_Short:      return TAG_Short.from_bytes(data_reader, endianness)
        case IdEnum.TAG_Int:        return TAG_Int.from_bytes(data_reader, endianness)
        case IdEnum.TAG_Long:       return TAG_Long.from_bytes(data_reader, endianness)
        case IdEnum.TAG_Float:      return TAG_Float.from_bytes(data_reader, endianness)
        case IdEnum.TAG_Double:     return TAG_Double.from_bytes(data_reader, endianness)
        case IdEnum.TAG_Byte_Array: return TAG_Byte_Array.from_bytes(data_reader, endianness)
        case IdEnum.TAG_String:     return TAG_String.from_bytes(data_reader, endianness)
        case IdEnum.TAG_List:       return TAG_List.from_bytes(data_reader, endianness)
        case IdEnum.TAG_Compound:   return TAG_Compound.from_bytes(data_reader, endianness)
        case IdEnum.TAG_Int_Array:  return TAG_Int_Array.from_bytes(data_reader, endianness)
        case IdEnum.TAG_Long_Array: return TAG_Long_Array.from_bytes(data_reader, endianness)
        case _:
            raise ValueError("Invalid content type: %i!" % (content_type))
