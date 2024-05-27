from typing import Callable

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.FunctionField as FunctionField
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.Normalizer as Normalizer
import Utilities.TypeVerifier as TypeVerifier


class NormalizerComponent(Component.Component):

    class_name_article = "a Normalizer"
    class_name = "Normalizer"

    my_properties = ComponentCapabilities.Capabilities(is_function=True, is_normalizer=True)

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
        self.final:Normalizer.Normalizer|None = None

        self.function_field = FunctionField.FunctionField(data["function_name"], ["function_name"])
        self.fields.extend([self.function_field])

    def set_component(self, components: dict[str, Component.Component], functions: dict[str, Callable]) -> None:
        super().set_component(components, functions)
        self.final = Normalizer.Normalizer(self.function_field.get_function(), self.dependencies)

    def check(self, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        exceptions = super().check(config)
        if not config.allow_normalizer_dependencies and len(self.dependencies) > 0:
            exceptions.append(ValueError("Normalizer \"%s\" has dependencies in an environment with no allowed normalizer dependencies!" % (self.name,)))
        return exceptions
