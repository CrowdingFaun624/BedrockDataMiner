from typing import Sequence

from Component.ComponentTyping import NormalizerStructureTypedDict
from Component.Field.ComponentListField import ComponentListField
from Component.Field.Field import Field
from Component.Structure.FunctionComponent import FUNCTION_PATTERN
from Component.Structure.WithinStructureComponent import WithinStructureComponent
from Structure.StructureTypes.NormalizerStructure import NormalizerStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class NormalizerStructureComponent(WithinStructureComponent[NormalizerStructure]):

    __slots__ = (
        "functions_field",
    )

    class_name = "Normalizer"
    structure_type = NormalizerStructure
    type_verifier = WithinStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("functions", True, UnionTypeVerifier(str, dict, ListTypeVerifier((str, dict), list))),
    ))

    def initialize_fields(self, data: NormalizerStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.functions_field = ComponentListField(data.get("functions"), FUNCTION_PATTERN, ("functions",), assume_type="Function")

        fields.append(self.functions_field)
        return fields


    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_normalizer_structure(
            functions=tuple(self.functions_field.map(lambda subcomponent: subcomponent.final)),
        )
