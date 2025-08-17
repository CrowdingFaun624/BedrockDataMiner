from typing import AbstractSet, Any, Mapping, NotRequired, Required, Sequence

from Component.Structure.MappingStructureComponent import (
    MappingStructureComponent,
    MappingStructureTypedDict,
)
from Component.Structure.StructureComponent import types_type_verifier
from Structure.Structure import Structure
from Structure.StructureTypes.DictStructure import DictStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class DictStructureTypedDict(MappingStructureTypedDict):
    allow_key_moves: NotRequired[bool]
    allow_same_key_optimization: NotRequired[bool | None]
    key_structure: NotRequired[Structure | None]
    key_weight: NotRequired[int]
    value_structure: Required[Structure | None]
    value_types: Required[type | Sequence[type]]
    value_weight: NotRequired[int]

def data_verify_function(data:DictStructureTypedDict) -> tuple[bool, str]:
    if data.get("key_weight", 1) == 0 and data.get("value_weight", 1) == 0:
        return False, "key weight and value weight cannot both be 0"
    return True, ""

class DictStructureComponent(MappingStructureComponent[DictStructure, DictStructureTypedDict]):

    type_name = "Dict"
    object_type = DictStructure
    abstract = False

    type_verifier = MappingStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("allow_key_moves", False, bool),
        TypedDictKeyTypeVerifier("allow_same_key_optimization", False, (bool, type(None))),
        TypedDictKeyTypeVerifier("key_structure", False, (Structure, type(None))),
        TypedDictKeyTypeVerifier("key_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
        TypedDictKeyTypeVerifier("value_structure", True, (Structure, type(None))),
        TypedDictKeyTypeVerifier("value_types", True, types_type_verifier),
        TypedDictKeyTypeVerifier("value_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
        function=data_verify_function,
    ))

    def link_final(self, fields: DictStructureTypedDict) -> None:
        super().link_final(fields)
        allow_same_key_optimization:bool|None = fields.get("allow_same_key_optimization")
        self.final.link_dict_structure(
            allow_key_moves=fields.get("allow_key_moves", True),
            allow_same_key_optimization=allow_same_key_optimization if allow_same_key_optimization is not None else fields.get("value_weight", self.final.VALUE_WEIGHT) == 0 or not fields.get("allow_key_moves", True),
            key_structure=fields.get("key_structure", None),
            key_weight=fields.get("key_weight", self.final.KEY_WEIGHT),
            value_structure=fields["value_structure"],
            value_types=fields["value_types"],
            value_weight=fields.get("value_weight", self.final.VALUE_WEIGHT),
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        self.final.finalize_dict_structure()
        return super().finalize(propagating_booleans, propagating_sets, trace)
