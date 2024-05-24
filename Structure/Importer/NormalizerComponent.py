from typing import Callable

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
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
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
    )

    def __init__(self, data:ComponentTyping.NormalizerTypedDict, name:str) -> None:
        self.verify_arguments(data, name)

        self.name = name
        self.dependencies = data.get("dependencies", [])
        self.function_name = data["function_name"]

        self.final:Normalizer.Normalizer|None = None
        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []

        self.children_has_normalizer = True

    def set_component(self, components: dict[str, Component.Component], functions: dict[str, Callable]) -> None:
        if self.function_name not in functions:
            raise KeyError("Function \"%s\", referenced in key \"function_name\" of %s \"%s\", does not exist!" % (self.function_name, self.class_name, self.name))
        self.final = Normalizer.Normalizer(functions[self.function_name], self.dependencies)

    def check(self, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        exceptions:list[Exception] = []
        if not config.allow_normalizer_dependencies and len(self.dependencies) > 0:
            exceptions.append(ValueError("Normalizer \"%s\" has dependencies in an environment with no allowed normalizer dependencies!" % (self.name,)))
        return exceptions
