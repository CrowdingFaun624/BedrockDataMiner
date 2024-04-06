from typing import Callable

import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Comparison.Normalizer as Normalizer
import Utilities.TypeVerifier as TypeVerifier

class NormalizerFunctionIntermediate(Intermediate.Intermediate):

    class_name_article = "a NormalizerFunction"
    class_name = "NormalizerFunction"

    my_properties = IntermediateCapabilities.Capabilities(is_function=True, is_normalizer_function=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("dependencies", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
            TypeVerifier.TypedDictKeyTypeVerifier("function_name", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int)
    )

    def __init__(self, data:ComparerTyping.NormalizerFunctionTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.dependencies = data["dependencies"]
        self.function_name = data["function_name"]

        self.final:Normalizer.Normalizer|None = None
        self.links_to_other_intermediates:list[Intermediate.Intermediate] = []
        self.parents:list[Intermediate.Intermediate] = []

        self.children_has_normalizer = True

    def set(self, intermediate_comparers: dict[str, Intermediate.Intermediate], functions: dict[str, Callable]) -> None:
        if self.function_name not in functions:
            raise KeyError("Function \"%s\", referenced in key \"function_name\" of %s \"%s\", does not exist!" % (self.function_name, self.class_name, self.name))
        self.final = Normalizer.Normalizer(functions[self.function_name], self.dependencies)
