from typing import Sequence

import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Field.FunctionField as FunctionField
import Component.Pattern as Pattern
import Component.Structure.FilterComponent as FilterComponent
import Structure.Normalizer as Normalizer
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

NORMALIZER_PATTERN:Pattern.Pattern["NormalizerComponent"] = Pattern.Pattern("is_normalizer")

class NormalizerComponent(Component.Component[Normalizer.Normalizer]):

    class_name = "Normalizer"
    my_capabilities = Capabilities.Capabilities(is_normalizer=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("filter", False, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("function_name", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "arguments",
        "children_has_normalizer",
        "function_field",
        "filter_field",
    )

    def initialize_fields(self, data: ComponentTyping.NormalizerTypedDict) -> Sequence[Field.Field]:
        self.variable_bools["children_has_normalizer"] = True
        self.arguments = data.get("arguments", {})

        self.function_field = FunctionField.FunctionField(data["function_name"], ("function_name",))
        self.filter_field = ComponentField.OptionalComponentField(data.get("filter", None), FilterComponent.FILTER_PATTERN, ("filter",))
        return (self.function_field, self.filter_field)

    def get_propagated_variables(self) -> tuple[dict[str, bool], dict[str, set]]:
        return {"children_has_normalizer": False}, {}

    def create_final(self, trace:Trace.Trace) -> Normalizer.Normalizer:
        return Normalizer.Normalizer(
            name=self.name,
            function=self.function_field.function,
            arguments=self.arguments,
        )

    def link_finals(self, trace:Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_subcomponents(
                filter=self.filter_field.map(lambda subcomponent: subcomponent.final),
            )
