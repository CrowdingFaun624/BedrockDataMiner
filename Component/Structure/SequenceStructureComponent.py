from typing import AbstractSet, Any, Mapping, NotRequired, Required, Sequence

from Component.Structure.IterableStructureComponent import (
    IterableStructureComponent,
    IterableStructureTypedDict,
)
from Component.Structure.StructureComponent import types_type_verifier
from Structure.Structure import Structure
from Structure.StructureTypes.SequenceStructure import SequenceStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class SequenceStructureTypedDict(IterableStructureTypedDict):
    addition_cost: NotRequired[float]
    deletion_cost: NotRequired[float]
    key_structure: NotRequired[Structure | None]
    key_weight: NotRequired[int]
    max_square_length: NotRequired[int]
    substitution_cost: NotRequired[float]
    value_structure: Required[Structure | None]
    value_types: Required[type | Sequence[type]]
    value_weight: NotRequired[int]

class SequenceStructureComponent(IterableStructureComponent[SequenceStructure, SequenceStructureTypedDict]):

    type_name = "Sequence"
    object_type = SequenceStructure
    abstract = False

    default_this_types = (list,)
    default_key_types = (int,)
    type_verifier = IterableStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("addition_cost", False, (float, int), lambda key, value: (value > 0, "must be positive")),
        TypedDictKeyTypeVerifier("deletion_cost", False, (float, int), lambda key, value: (value > 0, "must be positive")),
        TypedDictKeyTypeVerifier("key_structure", False, (Structure, type(None))),
        TypedDictKeyTypeVerifier("key_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
        TypedDictKeyTypeVerifier("max_square_length", False, int, lambda key, value: (value > 0, "must be positive")),
        TypedDictKeyTypeVerifier("substitution_cost", False, float, lambda key, value: (value > 0, "must be positive")),
        TypedDictKeyTypeVerifier("value_structure", True, (Structure, type(None))),
        TypedDictKeyTypeVerifier("value_types", True, types_type_verifier),
        TypedDictKeyTypeVerifier("value_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
    ))

    def link_final(self, fields: SequenceStructureTypedDict) -> None:
        super().link_final(fields)
        self.final.link_sequence_structure(
            addition_cost=fields.get("addition_cost", 1),
            deletion_cost=fields.get("deletion_cost", 1),
            key_structure=fields.get("key_structure", None),
            key_weight=fields.get("key_weight", self.final.KEY_WEIGHT),
            max_square_length=fields.get("max_square_length", 10000),
            substitution_cost=fields.get("substitution_cost", 4),
            value_structure=fields["value_structure"],
            value_types=fields["value_types"],
            value_weight=fields.get("value_weight", self.final.VALUE_WEIGHT),
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        self.final.finalize_sequence_structure()
        return super().finalize(propagating_booleans, propagating_sets, trace)
