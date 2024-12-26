import enum
import re
from typing import Literal, Protocol, TypedDict, TypeVar, cast

import mutf8

import Component.Types as Types
import Structure.Difference as D
import Utilities.CustomJson as CustomJson
import Utilities.Exceptions as Exceptions
import Utilities.Nbt.DataReader as DataReader
import Utilities.Nbt.Endianness as Endianness

NbtJsonTypedDict = TypedDict("NbtJsonTypedDict", {"$special_type": Literal["nbt"], "data": str})

class NbtCoder(CustomJson.Coder[NbtJsonTypedDict, "TAG"]):

    special_type_name = "nbt"

    @classmethod
    def decode(cls, data: NbtJsonTypedDict) -> "TAG":
        import Utilities.Nbt.NbtReader as NbtReader
        return NbtReader.unpack_snbt(data["data"])

    @classmethod
    def encode(cls, data: "TAG") -> NbtJsonTypedDict:
        return {"$special_type": "nbt", "data": str(data)}

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

a = TypeVar("a", covariant=True)
b = TypeVar("b")

class TAG(Protocol[a]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG": ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, str(self))

class TAG_End(TAG[None]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_End":
        return cls()

    def __str__(self) -> str:
        return "<END>"

    def __hash__(self) -> int:
        return hash(None)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, TAG_End)

    def __deepcopy__(self, memo) -> TAG:
        return self

@Types.register_decorator("TAG_Byte", json_coder=NbtCoder)
class TAG_Byte(int, TAG[int]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Byte":
        return cls(data_reader.unpack_tuple("b", 1, endianness))

    def __str__(self) -> str:
        return "%ib" % self

@Types.register_decorator("TAG_Short", json_coder=NbtCoder)
class TAG_Short(int, TAG[int]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Short":
        return cls(data_reader.unpack_tuple("h", 2, endianness))

    def __str__(self) -> str:
        return "%is" % self

@Types.register_decorator("TAG_Int", json_coder=NbtCoder)
class TAG_Int(int, TAG[int]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Int":
        return cls(data_reader.unpack_tuple("i", 4, endianness))

    def __str__(self) -> str:
        return "%i" % self

@Types.register_decorator("TAG_Long", json_coder=NbtCoder)
class TAG_Long(int, TAG[int]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Long":
        return cls(data_reader.unpack_tuple("q", 8, endianness))

    def __str__(self) -> str:
        return "%il" % self

@Types.register_decorator("TAG_Float", json_coder=NbtCoder)
class TAG_Float(float, TAG[float]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Float":
        return cls(data_reader.unpack_tuple("f", 4, endianness))

    def __str__(self) -> str:
        return "%ff" % self

@Types.register_decorator("TAG_Double", json_coder=NbtCoder)
class TAG_Double(float, TAG[float]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Double":
        return cls(data_reader.unpack_tuple("d", 8, endianness))

    def __str__(self) -> str:
        return "%f" % self

@Types.register_decorator("TAG_Byte_Array", requires_subcomponent=False, can_contain={TAG_Byte}, json_coder=NbtCoder)
class TAG_Byte_Array(list[TAG_Byte], TAG[list[TAG_Byte]]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Byte_Array":
        size:int = data_reader.unpack_tuple("i", 4, endianness)
        return cls([TAG_Byte.from_bytes(data_reader, endianness) for i in range(size)])

    def __str__(self) -> str:
        return "[B;" + ", ".join(str(item) for item in self) + "]"

@Types.register_decorator("TAG_String", json_coder=NbtCoder)
class TAG_String(str, TAG[str]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_String":
        size:int = data_reader.unpack_tuple("H", 2, endianness)
        output2:tuple[bytes] = data_reader.unpack("c" * size, size, endianness)
        try: # because of VibrationTests/event_splash_boat_on_bubble_column.mcstructure in 1.19.40.20
            return cls(mutf8.decode_modified_utf8(b"".join(output2)))
        except UnicodeDecodeError:
            return cls("")

    def __str__(self) -> str:
        return "\"%s\"" % escape_string(self)

    def __stringify__(self) -> str:
        # for DefaultDelegate
        return str(self)

@Types.register_decorator("TAG_List", json_coder=NbtCoder)
class TAG_List(list[TAG[b]], TAG[list[TAG[b]]]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_List":
        content_type:int = data_reader.unpack_tuple("b", 1, endianness)
        size:int = data_reader.unpack_tuple("i", 4, endianness)
        return cls([parse_object_from_bytes(data_reader, content_type, endianness) for i in range(size)])

    def __str__(self) -> str:
        return "[" + ", ".join(str(item) for item in self) + "]"

@Types.register_decorator("TAG_Compound", json_coder=NbtCoder)
class TAG_Compound(dict[str,TAG[b]], TAG[dict[str,TAG[b]]]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Compound":
        output:dict[str,TAG] = {}
        while True:
            key_name, value = parse_compound_item_from_bytes(data_reader, endianness)
            if isinstance(value, TAG_End) or key_name is None:
                break
            if key_name in output:
                raise Exceptions.CompoundDuplicateKeyError(key_name)
            output[key_name] = value
        return cls(output)

    def __str__(self) -> str:
        output = "{"
        for index, (key, value) in enumerate(self.items()):
            if self.should_enquote_key(key):
                output += "\"%s\"" % escape_string(key)
            else:
                output += str(key)
            output += ": "
            output += str(value)
            if index != len(self) - 1:
                output += ", "
        output += "}"
        return output

    def should_enquote_key(self, key:str, pattern=re.compile(r'[^a-zA-Z0-9._]').search) -> bool:
        if isinstance(key, D.Diff): return False
        if len(key) == 0: return True
        return bool(pattern(key))

@Types.register_decorator("TAG_Int_Array", requires_subcomponent=False, can_contain={TAG_Int}, json_coder=NbtCoder)
class TAG_Int_Array(list[TAG_Int], TAG[list[TAG_Int]]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Int_Array":
        size:int = data_reader.unpack_tuple("i", 4, endianness)
        return cls([TAG_Int.from_bytes(data_reader, endianness) for i in range(size)])

    def __str__(self) -> str:
        return "[I;" + ", ".join(str(item) for item in self) + "]"

@Types.register_decorator("TAG_Long_Array", requires_subcomponent=False, can_contain={TAG_Float}, json_coder=NbtCoder)
class TAG_Long_Array(list[TAG_Long], TAG[list[TAG_Long]]):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Long_Array":
        size:int = data_reader.unpack_tuple("i", 4, endianness)
        return cls([TAG_Long.from_bytes(data_reader, endianness) for i in range(size)])

    def __str__(self) -> str:
        return "[L;" + ", ".join(str(item) for item in self) + "]"

def escape_string(string:str) -> str:
    output = ""
    for char in string:
        match char:
            case "\"": output += "\\\""
            case "\\": output += "\\\\"
            case _: output += char
    return output

def parse_compound_item_from_bytes(data_reader:DataReader.DataReader, endianness:Endianness.End) -> tuple[str|None,TAG]:
    content_type:int = data_reader.unpack_tuple("b", 1, endianness)
    if content_type == IdEnum.TAG_End:
        return None, TAG_End.from_bytes(data_reader, endianness) # TAG_End has no name
    key_name = cast(TAG_String, parse_object_from_bytes(data_reader, IdEnum.TAG_String, endianness))
    value = parse_object_from_bytes(data_reader, content_type, endianness)
    return key_name, value

def parse_object_from_bytes(data_reader:DataReader.DataReader, content_type:int, endianness:Endianness.End) -> TAG:
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
            raise Exceptions.InvalidNbtContentType(content_type)
