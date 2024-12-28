import enum
import re
from math import floor
from typing import Literal, Protocol, TypedDict, cast

import mutf8

import _assets.scripts.Nbt.DataReader as DataReader
import _assets.scripts.Nbt.Endianness as Endianness
import _assets.scripts.Nbt.NbtExceptions as NbtExceptions
import Component.Types as Types
import Structure.Difference as D
import Utilities.CustomJson as CustomJson

NbtJsonTypedDict = TypedDict("NbtJsonTypedDict", {"$special_type": Literal["nbt"], "data": str})

class NbtCoder(CustomJson.Coder[NbtJsonTypedDict, "TAG"]):

    special_type_name = "nbt"

    @classmethod
    def decode(cls, data: NbtJsonTypedDict) -> "TAG":
        import _assets.scripts.Nbt.NbtReader as NbtReader
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

class TAG(Protocol):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG": ...

    def __str__(self) -> str: ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {str(self)}>"

class TAG_End(TAG):

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
class TAG_Byte(int, TAG):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Byte":
        return cls(data_reader.unpack_tuple("b", 1, endianness))

    def __str__(self) -> str:
        return f"{self:d}b"

@Types.register_decorator("TAG_Short", json_coder=NbtCoder)
class TAG_Short(int, TAG):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Short":
        return cls(data_reader.unpack_tuple("h", 2, endianness))

    def __str__(self) -> str:
        return f"{self:d}s"

@Types.register_decorator("TAG_Int", json_coder=NbtCoder)
class TAG_Int(int, TAG):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Int":
        return cls(data_reader.unpack_tuple("i", 4, endianness))

    def __str__(self) -> str:
        return f"{self:d}"

@Types.register_decorator("TAG_Long", json_coder=NbtCoder)
class TAG_Long(int, TAG):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Long":
        return cls(data_reader.unpack_tuple("q", 8, endianness))

    def __str__(self) -> str:
        return f"{self:d}l"

@Types.register_decorator("TAG_Float", json_coder=NbtCoder)
class TAG_Float(float, TAG):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Float":
        return cls(data_reader.unpack_tuple("f", 4, endianness))

    def __str__(self) -> str:
        if self % 1 == 0:
            return f"{floor(self):d}f"
        else:
            return f"{self:f}f"

@Types.register_decorator("TAG_Double", json_coder=NbtCoder)
class TAG_Double(float, TAG):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Double":
        return cls(data_reader.unpack_tuple("d", 8, endianness))

    def __str__(self) -> str:
        if self.is_integer():
            return f"{floor(self):d}.0"
        else:
            return f"{self:f}"

@Types.register_decorator("TAG_Byte_Array", requires_subcomponent=False, can_contain={TAG_Byte}, json_coder=NbtCoder)
class TAG_Byte_Array(list[TAG_Byte], TAG):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Byte_Array":
        size:int = data_reader.unpack_tuple("i", 4, endianness)
        return cls([TAG_Byte.from_bytes(data_reader, endianness) for i in range(size)])

    def __str__(self) -> str:
        return f"[B;{", ".join(str(item) for item in self)}]"

@Types.register_decorator("TAG_String", json_coder=NbtCoder)
class TAG_String(str, TAG):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_String":
        size:int = data_reader.unpack_tuple("H", 2, endianness)
        output2:tuple[bytes] = data_reader.unpack("c" * size, size, endianness)
        try: # because of VibrationTests/event_splash_boat_on_bubble_column.mcstructure in 1.19.40.20
            return cls(mutf8.decode_modified_utf8(b"".join(output2)))
        except UnicodeDecodeError:
            return cls("")

    def __str__(self) -> str:
        return f"\"{escape_string(self)}\""

    def __stringify__(self) -> str:
        # for DefaultDelegate
        return str(self)

@Types.register_decorator("TAG_List", json_coder=NbtCoder)
class TAG_List[b: TAG](list[b], TAG):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_List":
        content_type:int = data_reader.unpack_tuple("b", 1, endianness)
        size:int = data_reader.unpack_tuple("i", 4, endianness)
        return cls(cast(b, parse_object_from_bytes(data_reader, content_type, endianness)) for i in range(size))

    def __str__(self) -> str:
        return f"[{", ".join(str(item) for item in self)}]"

@Types.register_decorator("TAG_Compound", json_coder=NbtCoder)
class TAG_Compound[b: TAG](dict[str,b], TAG):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Compound":
        output:dict[str,b] = {}
        while True:
            key_name, value = parse_compound_item_from_bytes(data_reader, endianness)
            if isinstance(value, TAG_End) or key_name is None:
                break
            if key_name in output:
                raise NbtExceptions.CompoundDuplicateKeyError(key_name)
            output[key_name] = cast(b, value)
        return cls(output)

    def __str__(self) -> str:
        output:list[str] = ["{"]
        for index, (key, value) in enumerate(self.items()):
            if self.should_enquote_key(key):
                output.append(f"\"{escape_string(key)}\"")
            else:
                output.append(escape_string(key))
            output.append(": ")
            output.append(str(value))
            if index != len(self) - 1:
                output.append(", ")
        output.append("}")
        return "".join(output)

    def should_enquote_key(self, key:str, pattern=re.compile(r'[^a-zA-Z0-9._]').search) -> bool:
        if isinstance(key, D.Diff): return False
        if len(key) == 0: return True
        return bool(pattern(key))

@Types.register_decorator("TAG_Int_Array", requires_subcomponent=False, can_contain={TAG_Int}, json_coder=NbtCoder)
class TAG_Int_Array(list[TAG_Int], TAG):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Int_Array":
        size:int = data_reader.unpack_tuple("i", 4, endianness)
        return cls([TAG_Int.from_bytes(data_reader, endianness) for i in range(size)])

    def __str__(self) -> str:
        return f"[I;{", ".join(str(item) for item in self)}]"

@Types.register_decorator("TAG_Long_Array", requires_subcomponent=False, can_contain={TAG_Float}, json_coder=NbtCoder)
class TAG_Long_Array(list[TAG_Long], TAG):

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Long_Array":
        size:int = data_reader.unpack_tuple("i", 4, endianness)
        return cls([TAG_Long.from_bytes(data_reader, endianness) for i in range(size)])

    def __str__(self) -> str:
        return f"[L;{", ".join(str(item) for item in self)}]"

def escape_string(string:str) -> str:
    output:list[str] = []
    for char in string:
        match char:
            case "\"": output.append("\\\"")
            case "\\": output.append("\\\\")
            case _: output.append(char)
    return "".join(output)

def parse_compound_item_from_bytes[b:TAG=TAG](data_reader:DataReader.DataReader, endianness:Endianness.End) -> tuple[str|None,b]:
    content_type:int = data_reader.unpack_tuple("b", 1, endianness)
    if content_type == IdEnum.TAG_End:
        return None, cast(b, TAG_End.from_bytes(data_reader, endianness)) # TAG_End has no name
    key_name = cast(TAG_String, parse_object_from_bytes(data_reader, IdEnum.TAG_String, endianness))
    value = parse_object_from_bytes(data_reader, content_type, endianness)
    return key_name, cast(b, value)

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
            raise NbtExceptions.InvalidNbtContentType(content_type)
