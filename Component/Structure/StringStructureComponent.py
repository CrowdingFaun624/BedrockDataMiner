from typing import Callable, Sequence, cast

from Component.ComponentTyping import StringStructureTypedDict
from Component.Field.Field import Field
from Component.Field.FunctionField import OptionalFunctionField
from Component.Structure.AbstractPrimitiveStructureComponent import (
    AbstractPrimitiveStructureComponent,
)
from Structure.SimpleContainer import SCon
from Structure.StructureTypes.StringStructure import StringStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class StringStructureComponent(AbstractPrimitiveStructureComponent[StringStructure]):

    __slots__ = (
        "max_square_length",
        "similarity_function_field",
        "similarity_weight_function_field",
    )

    class_name = "String"
    structure_type = StringStructure
    default_this_types_name = ("str",)
    type_verifier = AbstractPrimitiveStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("max_square_length", False, int),
        TypedDictKeyTypeVerifier("similarity_function", False, str),
        TypedDictKeyTypeVerifier("similarity_weight_function", False, str),
    ))

    def initialize_fields(self, data: StringStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.max_square_length = data.get("max_square_length", 10000)

        self.similarity_function_field = OptionalFunctionField(data.get("similarity_function", None), ("similarity_function",))
        self.similarity_weight_function_field = OptionalFunctionField(data.get("similarity_weight_function", None), ("similarity_weight_function",))

        fields.extend((self.similarity_function_field, self.similarity_weight_function_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_string_structure(
                max_square_length=self.max_square_length,
                similarity_function=self.similarity_function_field.function if self.similarity_function_field.function is not None else cast(Callable[[SCon], str], lambda a: a.data),
                similarity_weight_function=self.similarity_weight_function_field.function if self.similarity_weight_function_field.function is not None else lambda a: [1 for i in a]
                # TODO: similarity_function cannot be None if this_types is not a str!
            )
