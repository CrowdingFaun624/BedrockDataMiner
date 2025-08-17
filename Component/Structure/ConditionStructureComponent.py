from typing import AbstractSet, Any, Mapping, Required, Sequence

from Component.Structure.PassthroughStructureComponent import (
    PassthroughStructureComponent,
    PassthroughStructureTypedDict,
)
from Structure.Key import Key
from Structure.StructureTypes.ConditionStructure import ConditionStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class ConditionStructureTypedDict(PassthroughStructureTypedDict):
    substructures: Required[Sequence[Key]]

class ConditionStructureComponent(PassthroughStructureComponent[ConditionStructure, ConditionStructureTypedDict]):

    type_name = "Condition"
    object_type = ConditionStructure
    abstract = False

    type_verifier = PassthroughStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("substructures", True, ListTypeVerifier(Key, list)),
    ))

    def link_final(self, fields: ConditionStructureTypedDict) -> None:
        super().link_final(fields)
        self.final.link_condition_structure(
            keys=fields["substructures"]
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        self.final.finalize_condition_structure()
        return False
