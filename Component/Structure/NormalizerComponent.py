from typing import Sequence

from Component.Capabilities import Capabilities
from Component.Component import Component
from Component.ComponentFunctions import function_type_verifiers
from Component.ComponentTyping import NormalizerTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field
from Component.Field.FunctionField import FunctionField
from Component.Pattern import Pattern
from Component.Structure.FilterComponent import FILTER_PATTERN
from Structure.Normalizer import Normalizer
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier

NORMALIZER_PATTERN:Pattern["NormalizerComponent"] = Pattern("is_normalizer")

class NormalizerComponent(Component[Normalizer]):

    class_name = "Normalizer"
    my_capabilities = Capabilities(is_normalizer=True)

    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("arguments", False, dict),
        TypedDictKeyTypeVerifier("filter", False, (str, dict, type(None))),
        TypedDictKeyTypeVerifier("function_name", True, str),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "arguments",
        "children_has_normalizer",
        "function_field",
        "filter_field",
    )

    def initialize_fields(self, data: NormalizerTypedDict) -> Sequence[Field]:
        self.variable_bools["children_has_normalizer"] = True
        self.arguments = data.get("arguments", {})

        self.function_field = FunctionField(data["function_name"], ("function_name",))
        self.filter_field = OptionalComponentField(data.get("filter", None), FILTER_PATTERN, ("filter",))
        return (self.function_field, self.filter_field)

    def get_propagated_variables(self) -> tuple[dict[str, bool], dict[str, set]]:
        return {"children_has_normalizer": False}, {}

    def create_final(self, trace:Trace) -> Normalizer:
        return Normalizer(
            name=self.name,
            function=self.function_field.function,
            arguments=self.arguments,
        )

    def link_finals(self, trace:Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_subcomponents(
                filter=self.filter_field.map(lambda subcomponent: subcomponent.final),
            )

    def check(self, trace: Trace) -> None:
        super().check(trace)
        if (type_verifier := function_type_verifiers.get(self.function_field.function, None)) is not None:
            type_verifier.verify(self.arguments, trace)
