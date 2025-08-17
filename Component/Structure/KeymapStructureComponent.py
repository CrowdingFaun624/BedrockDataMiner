from typing import AbstractSet, Any, Mapping, NotRequired

from Component.Structure.MappingStructureComponent import (
    MappingStructureComponent,
    MappingStructureTypedDict,
)
from Structure.Key import Key
from Structure.Structure import Structure
from Structure.StructureTypes.KeymapStructure import KeymapStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class KeymapStructureTypedDict(MappingStructureTypedDict):
    allow_key_moves: NotRequired[bool]
    key_structure: NotRequired[Structure | None]
    key_weight: NotRequired[int]
    keys: NotRequired[Mapping[str, Key]]
    value_weight: NotRequired[int | None]

class KeymapStructureComponent(MappingStructureComponent[KeymapStructure, KeymapStructureTypedDict]):

    type_name = "Keymap"
    object_type = KeymapStructure
    abstract = False

    type_verifier = MappingStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("allow_key_moves", False, bool),
        TypedDictKeyTypeVerifier("key_structure", False, (Structure, type(None))),
        TypedDictKeyTypeVerifier("key_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
        TypedDictKeyTypeVerifier("keys", False, DictTypeVerifier(dict, str, Key)),
        TypedDictKeyTypeVerifier("value_weight", False, int, lambda key, value: (value >= 0, "must be positive"))
    ))

    def link_final(self, fields: KeymapStructureTypedDict) -> None:
        super().link_final(fields)
        value_weight = fields.get("value_weight", self.final.VALUE_WEIGHT)
        if value_weight is None: value_weight = self.final.VALUE_WEIGHT
        self.final.link_keymap_structure(
            allow_key_moves=fields.get("allow_key_moves", False),
            allow_same_key_optimization=True,
            key_structure=fields.get("key_structure", None),
            key_weight=fields.get("key_weight", self.final.KEY_WEIGHT),
            keys=fields.get("keys", {}),
            value_weight=value_weight,
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        # because of VolumeDelegate, there is a need to finalize the higher Structure class first so that the
        # value Structures are available to the Delegate during its finalization.
        self.final.finalize_keymap_structure()
        return super().finalize(propagating_booleans, propagating_sets, trace)
