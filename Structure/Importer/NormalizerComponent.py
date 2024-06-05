import Structure.Importer.Capabilities as Capabilities
import Structure.Importer.Component as Component
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.FunctionField as FunctionField
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.Normalizer as Normalizer
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class NormalizerComponent(Component.Component[Normalizer.Normalizer]):

    class_name_article = "a Normalizer"
    class_name = "Normalizer"

    my_capabilities = Capabilities.Capabilities(is_function=True, is_normalizer=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("dependencies", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("function_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
    )

    def __init__(self, data:ComponentTyping.NormalizerTypedDict, name:str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)

        self.dependencies = data.get("dependencies", [])
        self.children_has_normalizer = True
        self.children_has_normalizer_dependencies = (len(self.dependencies) > 0)

        self.function_field = FunctionField.FunctionField(data["function_name"], ["function_name"])
        self.fields.extend([self.function_field])

    def create_final(self) -> None:
        self.final = Normalizer.Normalizer(self.function_field.get_function(), self.dependencies)

    def check(self, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        exceptions = super().check(config)
        if not config.allow_normalizer_dependencies and len(self.dependencies) > 0:
            exceptions.append(Exceptions.ComponentConfigError(self, "by having dependencies in an environment with no normalizer dependencies allowed"))
        return exceptions
