import copy
import enum
import re
from typing import Generic, Iterable, Iterator, Mapping, TypeVar

import mutf8

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

    def __init__(self, value:a, *, hash:int|None=None) -> None:
        self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG": ...

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, self.__class__) and self.value == __value.value

    def __str__(self) -> str: ...

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, str(self))

    def __deepcopy__(self, memo) -> "TAG":
        return type(self)(copy.deepcopy(self.value))

class TAG_End(TAG[None]):

    value = None

    def __init__(self, value:None=None, *, hash:int|None=None) -> None:
        self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_End":
        return cls(None)

    def __str__(self) -> str:
        return "<END>"

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, TAG_End)

    def __deepcopy__(self, memo) -> TAG:
        return self

class TAG_Byte(TAG[int], int):

    def __init__(self, value:int=int(), *, hash:int|None=None) -> None:
        self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Byte":
        return cls(data_reader.unpack_tuple("b", 1, endianness))

    def __hash__(self) -> int:
        return hash(self.value)

    def __gt__(self, value: int) -> bool:
        return self.value > value

    def __lt__(self, value: int) -> bool:
        return self.value < value

    def __eq__(self, __value: object) -> bool:
        return self.value == __value

    def __index__(self) -> int:
        return self.value.__index__()

    def __str__(self) -> str:
        return "%ib" % self.value

    def __deepcopy__(self, memo) -> TAG:
        return self

class TAG_Short(TAG[int], int):

    def __init__(self, value:int=int(), *, hash:int|None=None) -> None:
        self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Short":
        return cls(data_reader.unpack_tuple("h", 2, endianness))

    def __hash__(self) -> int:
        return hash(self.value)

    def __gt__(self, value: int) -> bool:
        return self.value > value

    def __lt__(self, value: int) -> bool:
        return self.value < value

    def __eq__(self, __value: object) -> bool:
        return self.value == __value

    def __index__(self) -> int:
        return self.value.__index__()

    def __str__(self) -> str:
        return "%is" % self.value

    def __deepcopy__(self, memo) -> TAG:
        return self

class TAG_Int(TAG[int], int):

    def __init__(self, value:int=int(), *, hash:int|None=None) -> None:
        self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Int":
        return cls(data_reader.unpack_tuple("i", 4, endianness))

    def __hash__(self) -> int:
        return hash(self.value)

    def __gt__(self, value: int) -> bool:
        return self.value > value

    def __lt__(self, value: int) -> bool:
        return self.value < value

    def __eq__(self, __value: object) -> bool:
        return self.value == __value

    def __index__(self) -> int:
        return self.value.__index__()

    def __str__(self) -> str:
        return "%i" % self.value

    def __deepcopy__(self, memo) -> TAG:
        return self

class TAG_Long(TAG[int], int):

    def __init__(self, value:int=int(), *, hash:int|None=None) -> None:
        self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Long":
        return cls(data_reader.unpack_tuple("q", 8, endianness))

    def __hash__(self) -> int:
        return hash(self.value)

    def __gt__(self, value: int) -> bool:
        return self.value > value

    def __lt__(self, value: int) -> bool:
        return self.value < value

    def __eq__(self, __value: object) -> bool:
        return self.value == __value

    def __index__(self) -> int:
        return self.value.__index__()

    def __str__(self) -> str:
        return "%il" % self.value

    def __deepcopy__(self, memo) -> TAG:
        return self

class TAG_Float(TAG[float], float):

    def __init__(self, value:float=float(), *, hash:int|None=None) -> None:
        self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Float":
        return cls(data_reader.unpack_tuple("f", 4, endianness))

    def __hash__(self) -> int:
        return hash(self.value)

    def __gt__(self, value: int) -> bool:
        return self.value > value

    def __lt__(self, value: int) -> bool:
        return self.value < value

    def __eq__(self, __value: object) -> bool:
        return self.value == __value

    def __str__(self) -> str:
        return "%ff" % self.value

    def __deepcopy__(self, memo) -> TAG:
        return self

class TAG_Double(TAG[float], float):

    def __init__(self, value:float=float(), *, hash:int|None=None) -> None:
        self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Double":
        return cls(data_reader.unpack_tuple("d", 8, endianness))

    def __hash__(self) -> int:
        return hash(self.value)

    def __gt__(self, value: int) -> bool:
        return self.value > value

    def __lt__(self, value: int) -> bool:
        return self.value < value

    def __eq__(self, __value: object) -> bool:
        return self.value == __value

    def __str__(self) -> str:
        return "%f" % self.value

    def __deepcopy__(self, memo) -> TAG:
        return self

class TAG_Byte_Array(TAG[list[TAG_Byte]]):

    def __init__(self, value:list[TAG_Byte]|None=None, *, hash:int|None=None) -> None:
        if value is None:
            self.value = []
        else:
            self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Byte_Array":
        size:int = data_reader.unpack_tuple("i", 4, endianness)
        return cls([TAG_Byte.from_bytes(data_reader, endianness) for i in range(size)])

    def __str__(self) -> str:
        return "[B;" + ", ".join(str(item) for item in self.value) + "]"

    def __add__(self, __object:list[TAG_Byte]) -> "TAG_Byte_Array":
        return TAG_Byte_Array(self.value + __object)

    def __contains__(self, __object:object) -> bool:
        return __object in self.value

    def __delitem__(self, __index:int) -> None:
        del self.value[__index]

    def __getitem__(self, __index:int) -> TAG_Byte:
        return self.value[__index]

    def __iadd__(self, __object:list[TAG_Byte]) -> None:
        self.value += __object

    def __imul__(self, len:int) -> None:
        self.value *= len

    def __iter__(self) -> Iterator[TAG_Byte]:
        return iter(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __mul__(self, __len:int) -> "TAG_Byte_Array":
        return TAG_Byte_Array(self.value * __len)

    def __setitem__(self, __index:int, __object:TAG_Byte) -> None:
        self.value[__index] = __object

    def append(self, __object:TAG_Byte) -> None:
        self.value.append(__object)

    def clear(self) -> None:
        self.clear()

    def copy(self) -> "TAG_Byte_Array":
        return TAG_Byte_Array(self.value.copy())

    def count(self, __object:TAG_Byte) -> int:
        return self.value.count(__object)

    def extend(self, __object:list[TAG_Byte]) -> None:
        self.value.extend(__object)

    def index(self, __value:TAG_Byte) -> int:
        return self.value.index(__value)

    def insert(self, __index:int, __object:TAG_Byte) -> None:
        self.value.insert(__index, __object)

    def pop(self, __index:int=-1) -> TAG_Byte:
        return self.value.pop(__index)

    def remove(self, __object:TAG_Byte) -> None:
        self.value.remove(__object)

    def reverse(self) -> None:
        self.value.reverse()

    def sort(self) -> None:
        self.value.sort(key=lambda item: item.value)

class TAG_String(TAG[str], str):

    def __init__(self, value:str=str(), *, hash:int|None=None) -> None:
        self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_String":
        size:int = data_reader.unpack_tuple("H", 2, endianness)
        output2:tuple[bytes] = data_reader.unpack("c" * size, size, endianness)
        try: # because of VibrationTests/event_splash_boat_on_bubble_column.mcstructure in 1.19.40.20
            return cls(mutf8.decode_modified_utf8(b"".join(output2)))
        except UnicodeDecodeError:
            return cls("")

    def __str__(self) -> str:
        return "\"%s\"" % escape_string(self.value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __deepcopy__(self, memo) -> TAG:
        return self

class TAG_List(TAG[list[TAG]]):

    def __init__(self, value:list[TAG]|None=None, *, hash:int|None=None) -> None:
        if value is None:
            self.value = []
        else:
            self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_List":
        content_type:int = data_reader.unpack_tuple("b", 1, endianness)
        size:int = data_reader.unpack_tuple("i", 4, endianness)
        return cls([parse_object_from_bytes(data_reader, content_type, endianness) for i in range(size)])

    def __str__(self) -> str:
        return "[" + ", ".join(str(item) for item in self.value) + "]"

    def __add__(self, __object:list[TAG]) -> "TAG_List":
        return TAG_List(self.value + __object)

    def __contains__(self, __object:object) -> bool:
        return __object in self.value

    def __delitem__(self, __index:int) -> None:
        del self.value[__index]

    def __getitem__(self, __index:int) -> TAG:
        return self.value[__index]

    def __iadd__(self, __object:list[TAG]) -> None:
        self.value += __object

    def __imul__(self, len:int) -> None:
        self.value *= len

    def __iter__(self) -> Iterator[TAG]:
        return iter(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __mul__(self, __len:int) -> "TAG_List":
        return TAG_List(self.value * __len)

    def __setitem__(self, __index:int, __object:TAG) -> None:
        self.value[__index] = __object

    def append(self, __object:TAG) -> None:
        self.value.append(__object)

    def clear(self) -> None:
        self.clear()

    def copy(self) -> "TAG_List":
        return TAG_List(self.value.copy())

    def count(self, __object:TAG) -> int:
        return self.value.count(__object)

    def extend(self, __object:list[TAG]) -> None:
        self.value.extend(__object)

    def index(self, __value:TAG) -> int:
        return self.value.index(__value)

    def insert(self, __index:int, __object:TAG) -> None:
        self.value.insert(__index, __object)

    def pop(self, __index:int=-1) -> TAG:
        return self.value.pop(__index)

    def remove(self, __object:TAG) -> None:
        self.value.remove(__object)

    def reverse(self) -> None:
        self.value.reverse()

    def sort(self) -> None:
        self.value.sort(key=lambda item: item.value)

class TAG_Compound(TAG[dict[str,TAG]]):

    def __init__(self, value:dict[str,TAG]|None=None, *, hash:int|None=None) -> None:
        if value is None:
            self.value = {}
        else:
            self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Compound":
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

    def should_enquote_key(self, key:str, pattern=re.compile(r'[^a-zA-Z0-9._]').search) -> bool:
        if len(key) == 0: return True
        return bool(pattern(key))

    def __contains__(self, __value:object) -> bool:
        return __value in self.value

    def __delitem__(self, __key:str) -> None:
        del self.value[__key]

    def __getitem__(self, __key:str) -> TAG:
        return self.value[__key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __setitem__(self, __key:str, __value:TAG[a]) -> None:
        self.value[__key] = __value

    def clear(self) -> None:
        self.value.clear()

    def copy(self) -> "TAG_Compound":
        return TAG_Compound(self.value.copy())

    @classmethod
    def fromkeys(cls, __iterable: Iterable[str], __value:TAG[a]|None = None) -> "TAG_Compound":
        return TAG_Compound(dict.fromkeys(__iterable, __value)) # type: ignore

    def get(self, __key:str, default:a=None) -> TAG|a:
        return self.value.get(__key, default)

    def items(self) -> Iterable[tuple[str,TAG]]:
        return self.value.items()

    def keys(self) -> Iterable[str]:
        return self.value.keys()

    def pop(self, __key:str) -> TAG:
        return self.value.pop(__key)

    def popitem(self) -> tuple[str, TAG]:
        return self.value.popitem()

    def setdefault(self, __key:str, __value:TAG[a]) -> TAG[a]:
        return self.value.setdefault(__key, __value)

    def update(self, __value:Mapping[str,TAG[a]]) -> None:
        self.value.update(__value)

    def values(self) -> Iterable[TAG]:
        return self.value.values()

class TAG_Int_Array(TAG[list[TAG_Int]]):

    def __init__(self, value:list[TAG_Int]|None=None, *, hash:int|None=None) -> None:
        if value is None:
            self.value = []
        else:
            self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Int_Array":
        size:int = data_reader.unpack_tuple("i", 4, endianness)
        return cls([TAG_Int.from_bytes(data_reader, endianness) for i in range(size)])

    def __str__(self) -> str:
        return "[I;" + ", ".join(str(item) for item in self.value) + "]"

    def __add__(self, __object:list[TAG_Int]) -> "TAG_Int_Array":
        return TAG_Int_Array(self.value + __object)

    def __contains__(self, __object:object) -> bool:
        return __object in self.value

    def __delitem__(self, __index:int) -> None:
        del self.value[__index]

    def __getitem__(self, __index:int) -> TAG_Int:
        return self.value[__index]

    def __iadd__(self, __object:list[TAG_Int]) -> None:
        self.value += __object

    def __imul__(self, len:int) -> None:
        self.value *= len

    def __iter__(self) -> Iterator[TAG_Int]:
        return iter(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __mul__(self, __len:int) -> "TAG_Int_Array":
        return TAG_Int_Array(self.value * __len)

    def __setitem__(self, __index:int, __object:TAG_Int) -> None:
        self.value[__index] = __object

    def append(self, __object:TAG_Int) -> None:
        self.value.append(__object)

    def clear(self) -> None:
        self.clear()

    def copy(self) -> "TAG_Int_Array":
        return TAG_Int_Array(self.value.copy())

    def count(self, __object:TAG_Int) -> int:
        return self.value.count(__object)

    def extend(self, __object:list[TAG_Int]) -> None:
        self.value.extend(__object)

    def index(self, __value:TAG_Int) -> int:
        return self.value.index(__value)

    def insert(self, __index:int, __object:TAG_Int) -> None:
        self.value.insert(__index, __object)

    def pop(self, __index:int=-1) -> TAG:
        return self.value.pop(__index)

    def remove(self, __object:TAG_Int) -> None:
        self.value.remove(__object)

    def reverse(self) -> None:
        self.value.reverse()

    def sort(self) -> None:
        self.value.sort(key=lambda item: item.value)

class TAG_Long_Array(TAG[list[TAG_Long]]):

    def __init__(self, value:list[TAG_Long]|None=None, *, hash:int|None=None) -> None:
        if value is None:
            self.value = []
        else:
            self.value = value
        self.hash = hash

    @classmethod
    def from_bytes(cls, data_reader:DataReader.DataReader, endianness:Endianness.End) -> "TAG_Long_Array":
        size:int = data_reader.unpack_tuple("i", 4, endianness)
        return cls([TAG_Long.from_bytes(data_reader, endianness) for i in range(size)])

    def __str__(self) -> str:
        return "[L;" + ", ".join(str(item) for item in self.value) + "]"

    def __add__(self, __object:list[TAG_Long]) -> "TAG_Long_Array":
        return TAG_Long_Array(self.value + __object)

    def __contains__(self, __object:object) -> bool:
        return __object in self.value

    def __delitem__(self, __index:int) -> None:
        del self.value[__index]

    def __getitem__(self, __index:int) -> TAG_Long:
        return self.value[__index]

    def __iadd__(self, __object:list[TAG_Long]) -> None:
        self.value += __object

    def __imul__(self, len:int) -> None:
        self.value *= len

    def __iter__(self) -> Iterator[TAG_Long]:
        return iter(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __mul__(self, __len:int) -> "TAG_Long_Array":
        return TAG_Long_Array(self.value * __len)

    def __setitem__(self, __index:int, __object:TAG_Long) -> None:
        self.value[__index] = __object

    def append(self, __object:TAG_Long) -> None:
        self.value.append(__object)

    def clear(self) -> None:
        self.clear()

    def copy(self) -> "TAG_Long_Array":
        return TAG_Long_Array(self.value.copy())

    def count(self, __object:TAG_Long) -> int:
        return self.value.count(__object)

    def extend(self, __object:list[TAG_Long]) -> None:
        self.value.extend(__object)

    def index(self, __value:TAG_Long) -> int:
        return self.value.index(__value)

    def insert(self, __index:int, __object:TAG_Long) -> None:
        self.value.insert(__index, __object)

    def pop(self, __index:int=-1) -> TAG_Long:
        return self.value.pop(__index)

    def remove(self, __object:TAG_Long) -> None:
        self.value.remove(__object)

    def reverse(self) -> None:
        self.value.reverse()

    def sort(self) -> None:
        self.value.sort(key=lambda item: item.value)

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
    key_name:str = parse_object_from_bytes(data_reader, IdEnum.TAG_String, endianness).value
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
            raise ValueError("Invalid content type: %i!" % (content_type))
