from typing import Callable, Sequence, cast

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.FunctionField as FunctionField
import Component.Structure.AbstractPrimitiveStructureComponent as AbstractPrimitiveStructureComponent
import Structure.SimpleContainer as SCon
import Structure.StructureTypes.NumberStructure as NumberStructure
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier


class NumberStructureComponent(AbstractPrimitiveStructureComponent.AbstractPrimitiveStructureComponent[NumberStructure.NumberStructure]):

    __slots__ = (
        "normal_value",
        "similarity_function_field",
    )

    class_name = "Number"
    structure_type = NumberStructure.NumberStructure
    default_this_types_name = ("int",)
    type_verifier = AbstractPrimitiveStructureComponent.AbstractPrimitiveStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("normal_value", True, (float, int), lambda key, value: (value > 0, "must be positive")),
        TypeVerifier.TypedDictKeyTypeVerifier("similarity_function", False, str),
    ))

    def initialize_fields(self, data: ComponentTyping.NumberStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.normal_value = data["normal_value"]

        self.similarity_function_field = FunctionField.OptionalFunctionField(data.get("similarity_function", None), ("similarity_function",))

        fields.append(self.similarity_function_field)
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_number_structure(
                normal_value=self.normal_value,
                similarity_function=self.similarity_function_field.function if self.similarity_function_field.function is not None else cast(Callable[[SCon.SCon], float], lambda a: a.data),
                # TODO: similarity_function cannot be None if this_types is not an int or float!
            )
