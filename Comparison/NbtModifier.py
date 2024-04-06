from typing import Any

import Comparison.ComparerSection as ComparerSection
import Comparison.Modifier as Modifier
import Comparison.Trace as Trace
import Utilities.Nbt.DataReader as DataReader
import Utilities.Nbt.Endianness as Endianness
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes

def get_endianness(endianness:str|None) -> Endianness.End|None:
    return None if endianness is None else (Endianness.End.BIG if endianness == "big" else Endianness.End.LITTLE)

content_types:list[type[NbtTypes.TAG]] = [
    NbtTypes.TAG_End,
    NbtTypes.TAG_Byte,
    NbtTypes.TAG_Short,
    NbtTypes.TAG_Int,
    NbtTypes.TAG_Long,
    NbtTypes.TAG_Float,
    NbtTypes.TAG_Double,
    NbtTypes.TAG_Byte_Array,
    NbtTypes.TAG_String,
    NbtTypes.TAG_List,
    NbtTypes.TAG_Compound,
    NbtTypes.TAG_Int_Array,
    NbtTypes.TAG_Long_Array,
]

class NbtModifier(Modifier.Modifier):

    def __init__(self, default_endianness:Endianness.End|None, *, keys_endianness:dict[str,Endianness.End|None]|None=None) -> None:
        self.default_endianness = default_endianness
        self.keys_endianness = keys_endianness
        self.comparer_section:ComparerSection.ComparerSection|None = None

    def choose_child_endianness(self, fallback_endianness:Endianness.End, key:str|None=None) -> Endianness.End:
        if key is not None and self.keys_endianness is not None:
            endianness = self.keys_endianness.get(key)
            if endianness is not None:
                return endianness
        if self.default_endianness is not None:
            return self.default_endianness
        return fallback_endianness

    def choose_comparer(self, key:str|int, content_type:int, data:DataReader.DataReader, endianness:Endianness.End, trace:Trace.Trace) -> ComparerSection.ComparerSection|None:
        exception = None
        try:
            assert self.comparer_section is not None
            return self.comparer_section.choose_comparer_flat(key, content_types[content_type], trace)
        except Exception as e:
            exception = e
            exception.args = tuple(list(exception.args) + [str(NbtTypes.parse_object_from_bytes(data, content_type, endianness))])
        raise exception

    def parse_object(self, data:DataReader.DataReader, content_type:int, endianness:Endianness.End, trace:Trace.Trace) -> NbtTypes.TAG:
        endianness = self.choose_child_endianness(endianness)
        match content_type:
            case NbtTypes.IdEnum.TAG_End:        return NbtTypes.TAG_End(None)
            case NbtTypes.IdEnum.TAG_Byte:       return NbtTypes.TAG_Byte.from_bytes(data, endianness)
            case NbtTypes.IdEnum.TAG_Short:      return NbtTypes.TAG_Short.from_bytes(data, endianness)
            case NbtTypes.IdEnum.TAG_Int:        return NbtTypes.TAG_Int.from_bytes(data, endianness)
            case NbtTypes.IdEnum.TAG_Long:       return NbtTypes.TAG_Long.from_bytes(data, endianness)
            case NbtTypes.IdEnum.TAG_Float:      return NbtTypes.TAG_Float.from_bytes(data, endianness)
            case NbtTypes.IdEnum.TAG_Double:     return NbtTypes.TAG_Double.from_bytes(data, endianness)
            case NbtTypes.IdEnum.TAG_Byte_Array: return NbtTypes.TAG_Byte_Array.from_bytes(data, endianness)
            case NbtTypes.IdEnum.TAG_String:     return NbtTypes.TAG_String.from_bytes(data, endianness)
            case NbtTypes.IdEnum.TAG_List:       return self.parse_tag_list(data, endianness, trace)
            case NbtTypes.IdEnum.TAG_Compound:   return self.parse_tag_compound(data, endianness, trace)
            case NbtTypes.IdEnum.TAG_Int_Array:  return NbtTypes.TAG_Int_Array.from_bytes(data, endianness)
            case NbtTypes.IdEnum.TAG_Long_Array: return NbtTypes.TAG_Long_Array.from_bytes(data, endianness)
            case _:
                raise ValueError("Invalid content type %i!" % (content_type))

    def parse_compound_item(self, data:DataReader.DataReader, endianness:Endianness.End, trace:Trace.Trace) -> tuple[str|None,NbtTypes.TAG]:
        content_type:int = data.unpack_tuple("b", 1, endianness)
        if content_type == NbtTypes.IdEnum.TAG_End:
            return None, NbtTypes.TAG_End(None)
        key_name = NbtTypes.TAG_String.from_bytes(data, endianness).value

        comparer = self.choose_comparer(key_name, content_type, data, endianness, trace)
        child_endianness = self.choose_child_endianness(endianness, key_name)
        assert self.comparer_section is not None
        if comparer is None or not isinstance(comparer.modifier, NbtModifier):
            return key_name, NbtTypes.parse_object_from_bytes(data, content_type, child_endianness)
        else:
            return key_name, comparer.modifier.parse_object(data, content_type, child_endianness, trace.copy(self.comparer_section.name, key_name))

    def parse_tag_list(self, data:DataReader.DataReader, endianness:Endianness.End, trace:Trace.Trace) -> NbtTypes.TAG_List:
        content_type:int = data.unpack_tuple("b", 1, endianness)
        comparer = self.choose_comparer(0, content_type, data, endianness, trace)
        size:int = data.unpack_tuple("i", 4, endianness)
        output:list[NbtTypes.TAG] = []
        assert self.comparer_section is not None
        for i in range(size):
            if comparer is None or not isinstance(comparer.modifier, NbtModifier):
                output.append(NbtTypes.parse_object_from_bytes(data, content_type, endianness))
            else:
                output.append(comparer.modifier.parse_object(data, content_type, endianness, trace.copy(self.comparer_section.name, i)))
        return NbtTypes.TAG_List(output)

    def parse_tag_compound(self, data:DataReader.DataReader, endianness:Endianness.End, trace:Trace.Trace) -> NbtTypes.TAG_Compound:
        output:dict[str,NbtTypes.TAG] = {}
        while True:
            key_name, value = self.parse_compound_item(data, endianness, trace)
            if isinstance(value, NbtTypes.TAG_End):
                break
            if key_name in output:
                raise KeyError("Duplicate key \"%s\"!" % key_name)
            assert key_name is not None
            output[key_name] = value
        return NbtTypes.TAG_Compound(output)

    def base_modify(self, data:NbtReader.NbtBytes, trace:Trace.Trace) -> Any:
        if self.default_endianness is None:
            raise RuntimeError("Called `base_modify` on NbtModifier with no default endianness!")
        data_reader = DataReader.DataBytesReader(data.value)
        return self.parse_compound_item(data_reader, self.default_endianness, trace)[1]
