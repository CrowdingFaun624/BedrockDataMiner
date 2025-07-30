from typing import Callable, Sequence, cast

from Component.ComponentTyping import NumberStructureTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field
from Component.Structure.AbstractPrimitiveStructureComponent import (
    AbstractPrimitiveStructureComponent,
)
from Component.Structure.FunctionComponent import FUNCTION_PATTERN
from Structure.SimpleContainer import SCon
from Structure.StructureTypes.NumberStructure import NumberStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class NumberStructureComponent(AbstractPrimitiveStructureComponent[NumberStructure]):

    __slots__ = (
        "normal_value",
        "similarity_function_field",
    )

    class_name = "Number"
    structure_type = NumberStructure
    default_this_types_name = ("int",)
    type_verifier = AbstractPrimitiveStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("normal_value", True, (float, int), lambda key, value: (value > 0, "must be positive")),
        TypedDictKeyTypeVerifier("similarity_function", False, (str, dict, type(None))),
    ))

    def initialize_fields(self, data: NumberStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.normal_value = data["normal_value"]

        self.similarity_function_field = OptionalComponentField(data.get("similarity_function", None), FUNCTION_PATTERN, ("similarity_function",), assume_type="Function")

        fields.append(self.similarity_function_field)
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_number_structure(
            normal_value=self.normal_value,
            similarity_function=self.similarity_function_field.subcomponent.final if self.similarity_function_field.subcomponent is not None else cast(Callable[[SCon], float], lambda a: a.data),
            # TODO: similarity_function cannot be None if this_types is not an int or float!
        )
