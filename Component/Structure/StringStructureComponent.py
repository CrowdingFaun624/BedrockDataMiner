from typing import Callable, Sequence, cast

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.FunctionField as FunctionField
import Component.Structure.AbstractPrimitiveStructureComponent as AbstractPrimitiveStructureComponent
import Structure.SimpleContainer as SCon
import Structure.StructureTypes.StringStructure as StringStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class StringStructureComponent(AbstractPrimitiveStructureComponent.AbstractPrimitiveStructureComponent[StringStructure.StringStructure]):

    __slots__ = (
        "max_square_length",
        "similarity_function_field",
        "similarity_weight_function_field",
    )

    class_name = "String"
    structure_type = StringStructure.StringStructure
    default_this_types_name = ("str",)
    type_verifier = AbstractPrimitiveStructureComponent.AbstractPrimitiveStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("max_square_length", False, int),
        TypeVerifier.TypedDictKeyTypeVerifier("similarity_function", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("similarity_weight_function", False, str),
    ))

    def initialize_fields(self, data: ComponentTyping.StringStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.max_square_length = data.get("max_square_length", 10000)

        self.similarity_function_field = FunctionField.OptionalFunctionField(data.get("similarity_function", None), ("similarity_function",))
        self.similarity_weight_function_field = FunctionField.OptionalFunctionField(data.get("similarity_weight_function", None), ("similarity_weight_function",))

        fields.extend((self.similarity_function_field, self.similarity_weight_function_field))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_string_structure(
                max_square_length=self.max_square_length,
                similarity_function=self.similarity_function_field.function if self.similarity_function_field.function is not None else cast(Callable[[SCon.SCon], str], lambda a: a.data),
                similarity_weight_function=self.similarity_weight_function_field.function if self.similarity_weight_function_field.function is not None else lambda a: [1 for i in a]
                # TODO: similarity_function cannot be None if this_types is not a str!
            )
