from typing import TypeVar

import Component.Component as Component
import Structure.Structure as Structure
import Utilities.Nbt.NbtReader as NbtReader
import Utilities.Nbt.NbtTypes as NbtTypes

a = TypeVar("a", bound=Structure.Structure)

DEFAULT_TYPES:dict[str,type] = {
    "bool": bool,
    "dict": dict,
    "float": float,
    "int": int,
    "list": list,
    "null": type(None),
    "str": str,
    "volume_base": tuple, # Volume becomes a tuple with various contents upon being normalized
    "nbt_base": NbtReader.NbtBytes,
    "TAG_Byte": NbtTypes.TAG_Byte,
    "TAG_Short": NbtTypes.TAG_Short,
    "TAG_Int": NbtTypes.TAG_Int,
    "TAG_Long": NbtTypes.TAG_Long,
    "TAG_Float": NbtTypes.TAG_Float,
    "TAG_Double": NbtTypes.TAG_Double,
    "TAG_Byte_Array": NbtTypes.TAG_Byte_Array,
    "TAG_String": NbtTypes.TAG_String,
    "TAG_List": NbtTypes.TAG_List,
    "TAG_Compound": NbtTypes.TAG_Compound,
    "TAG_Int_Array": NbtTypes.TAG_Int_Array,
    "TAG_Long_Array": NbtTypes.TAG_Long_Array,
}
REQUIRES_SUBCOMPONENT_TYPES = set([dict, list, NbtTypes.TAG_Byte_Array, NbtTypes.TAG_List, NbtTypes.TAG_Compound, NbtTypes.TAG_Int_Array, NbtTypes.TAG_Long_Array])
SORTABLE_TYPES = set([bool, float, int, type(None), str, NbtTypes.TAG_Byte, NbtTypes.TAG_Double, NbtTypes.TAG_Float, NbtTypes.TAG_Int, NbtTypes.TAG_Long, NbtTypes.TAG_Short, NbtTypes.TAG_String])

ARBITRARY_ITERABLE_TYPES = set((list, tuple, NbtTypes.TAG_List))
"""Iterable that allows for arbitrary/any data inside."""
ITERABLE_TYPES = set((list, tuple, NbtTypes.TAG_List, NbtTypes.TAG_Byte_Array, NbtTypes.TAG_Int_Array, NbtTypes.TAG_Long_Array))
"""Any iterable."""
MAPPING_TYPES = set((dict, NbtTypes.TAG_Compound))
"""Any mapping."""
NBT_TYPES = set((
    NbtTypes.TAG_Byte,
    NbtTypes.TAG_Byte_Array,
    NbtTypes.TAG_Compound,
    NbtTypes.TAG_Double,
    NbtTypes.TAG_Float,
    NbtTypes.TAG_Int,
    NbtTypes.TAG_Int_Array,
    NbtTypes.TAG_List,
    NbtTypes.TAG_Long,
    NbtTypes.TAG_Long_Array,
    NbtTypes.TAG_Short,
    NbtTypes.TAG_String
))
"""Any NBT Tag."""

CONTAINMENT_TYPES:dict[type,set[type]] = {
    NbtTypes.TAG_Byte_Array: {NbtTypes.TAG_Byte},
    NbtTypes.TAG_Int_Array: {NbtTypes.TAG_Int},
    NbtTypes.TAG_Long_Array: {NbtTypes.TAG_Long},
}

class StructureComponent(Component.Component[a]):

    class_name_article = "a StructureComponent"
    class_name = "StructureComponent"
    my_type:set[type]
