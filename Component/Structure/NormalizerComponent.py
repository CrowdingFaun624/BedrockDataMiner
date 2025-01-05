import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.FunctionField as FunctionField
import Component.Version.Field.VersionRangeField as VersionRangeField
import Structure.Normalizer as Normalizer
import Utilities.TypeVerifier as TypeVerifier


class NormalizerComponent(Component.Component[Normalizer.Normalizer]):

    class_name_article = "a Normalizer"
    class_name = "Normalizer"
    children_has_normalizer_default = True
    my_capabilities = Capabilities.Capabilities(is_function=True, is_normalizer=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("function_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("version_range", "a list", False, TypeVerifier.ListTypeVerifier((str, type(None)), list, "a str or None", "a list", additional_function=lambda data: (len(data) == 2, "must be length 2"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    __slots__ = (
        "arguments",
        "children_has_normalizer",
        "function_field",
        "version_range_field",
    )

    def initialize_fields(self, data: ComponentTyping.NormalizerTypedDict) -> list[Field.Field]:
        self.arguments = data.get("arguments", {})

        self.function_field = FunctionField.FunctionField(data["function_name"], ["function_name"])
        self.version_range_field = VersionRangeField.VersionRangeField(data["version_range"][0], data["version_range"][1], ["version_range"]) if "version_range" in data else VersionRangeField.VersionRangeField(None, None, ["version_range"])
        return [self.function_field, self.version_range_field]

    def create_final(self) -> Normalizer.Normalizer:
        return Normalizer.Normalizer(
            name=self.name,
            function=self.function_field.function,
            arguments=self.arguments,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_subcomponents(
            version_range=self.version_range_field.final,
        )
        return exceptions
