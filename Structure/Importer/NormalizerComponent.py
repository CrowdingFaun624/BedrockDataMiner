from typing import Callable

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Normalizer as Normalizer
import Utilities.TypeVerifier as TypeVerifier

class NormalizerComponent(Component.Component):

    class_name_article = "a Normalizer"
    class_name = "Normalizer"

    my_properties = ComponentCapabilities.Capabilities(is_function=True, is_normalizer=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("dependencies", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
            TypeVerifier.TypedDictKeyTypeVerifier("function_name", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int)
    )

    def __init__(self, data:ComponentTyping.NormalizerTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.dependencies = data["dependencies"]
        self.function_name = data["function_name"]

        self.final:Normalizer.Normalizer|None = None
        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []

        self.children_has_normalizer = True

    def set(self, components: dict[str, Component.Component], functions: dict[str, Callable]) -> None:
        if self.function_name not in functions:
            raise KeyError("Function \"%s\", referenced in key \"function_name\" of %s \"%s\", does not exist!" % (self.function_name, self.class_name, self.name))
        self.final = Normalizer.Normalizer(functions[self.function_name], self.dependencies)
