from typing import AbstractSet, Any, Mapping, Required

from Component.Structure.PassthroughStructureComponent import (
    PassthroughStructureComponent,
    PassthroughStructureTypedDict,
)
from Structure.Function import Function
from Structure.Key import Key
from Structure.StructureTypes.SwitchStructure import SwitchStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)


class SwitchStructureTypedDict(PassthroughStructureTypedDict):
    switch_function: Required[Function]
    substructures: Required[Mapping[str, Key]]

class SwitchStructureComponent(PassthroughStructureComponent[SwitchStructure, SwitchStructureTypedDict]):

    type_name = "Switch"
    object_type = SwitchStructure
    abstract = False

    type_verifier = PassthroughStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("switch_function", True, Function),
        TypedDictKeyTypeVerifier("substructures", True, DictTypeVerifier(dict, str, Key)),
    ))

    def link_final(self, fields: SwitchStructureTypedDict) -> None:
        super().link_final(fields)
        self.final.link_switch_structure(
            keys=fields["substructures"],
            switch_function=fields["switch_function"],
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        self.final.finalize_switch_structure()
        return False
