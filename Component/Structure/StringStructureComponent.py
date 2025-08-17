from typing import NotRequired

from Component.Structure.PrimitiveStructureComponent import (
    PrimitiveStructureComponent,
    PrimitiveStructureTypedDict,
)
from Structure.Function import Function
from Structure.StructureTypes.StringStructure import StringStructure
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class StringStructureTypedDict(PrimitiveStructureTypedDict):
    max_square_length: NotRequired[int]
    similarity_function: NotRequired[Function | None]
    similarity_weight_function: NotRequired[Function | None]

class StringStructureComponent(PrimitiveStructureComponent[StringStructure, StringStructureTypedDict]):

    type_name = "String"
    object_type = StringStructure
    abstract = False

    default_types:tuple[type,...] = (str,)
    type_verifier = PrimitiveStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("max_square_length", False, int, lambda key, value: (value > 0, "must be positive")),
        TypedDictKeyTypeVerifier("similarity_function", False, (Function, type(None))),
        TypedDictKeyTypeVerifier("similarity_weight_function", False, (Function, type(None))),
    ))

    def link_final(self, fields: StringStructureTypedDict) -> None:
        super().link_final(fields)
        self.final.link_string_structure(
            max_square_length=fields.get("max_square_length", 10000),
            similarity_function=(lambda data: data.data) if (similarity_function := fields.get("similarity_function", None)) is None else similarity_function,
            similarity_weight_function=(lambda data: [1 for _ in data]) if (similarity_weight_function := fields.get("similarity_weight_function", None)) is None else similarity_weight_function,
        )
