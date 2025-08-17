from typing import Required, Sequence

from Component.Structure.WithinStructureComponent import (
    WithinStructureComponent,
    WithinStructureTypedDict,
)
from Structure.Function import Function
from Structure.StructureTypes.NormalizerStructure import NormalizerStructure
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class NormalizerStructureTypedDict(WithinStructureTypedDict):
    functions: Required[Function | Sequence[Function]]

def convert_functions_to_sequence(sequence:Function | Sequence[Function]) -> Sequence[Function]:
    return [sequence] if isinstance(sequence, Function) else sequence

class NormalizerStructureComponent(WithinStructureComponent[NormalizerStructure, NormalizerStructureTypedDict]):

    type_name = "Normalizer"
    object_type = NormalizerStructure
    abstract = False

    type_verifier = WithinStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("functions", True, UnionTypeVerifier(Function, ListTypeVerifier(Function, list))),
    ))

    def link_final(self, fields: NormalizerStructureTypedDict) -> None:
        super().link_final(fields)
        self.final.link_normalizer_structure(
            functions=convert_functions_to_sequence(fields["functions"]),
        )
