from typing import NotRequired, Required

from Component.Structure.PrimitiveStructureComponent import (
    PrimitiveStructureComponent,
    PrimitiveStructureTypedDict,
)
from Structure.Function import Function
from Structure.StructureTypes.NumberStructure import NumberStructure
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class NumberStructureTypedDict(PrimitiveStructureTypedDict):
    normal_value: Required[float]
    similarity_function: NotRequired[Function]

class NumberStructureComponent(PrimitiveStructureComponent[NumberStructure, NumberStructureTypedDict]):

    type_name = "Number"
    object_type = NumberStructure
    abstract = False

    default_types = (int,)
    type_verifier = PrimitiveStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("normal_value", True, (float, int), lambda key, value: (value > 0, "must be positive")),
        TypedDictKeyTypeVerifier("similarity_function", False, (Function, type(None))),
    ))

    def link_final(self, fields: NumberStructureTypedDict) -> None:
        super().link_final(fields)
        self.final.link_number_structure(
            normal_value=fields["normal_value"],
            similarity_function=(lambda data: data.data) if (similarity_function := fields.get("similarity_function", None)) is None else similarity_function,
        )
