from typing import Callable

import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.Normalizer as Normalizer

class NormalizerFunctionIntermediate(Intermediate.Intermediate):

    def __init__(self, data:ComparerTyping.NormalizerFunctionTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("dependencies", list, "a list", True),
            ("function_name", str, "a str", True),
            ("type", str, "a str", True),
        ])
        if data["type"] != "NormalizerFunction":
            raise ValueError("Key \"type\" of Main \"%s\" is not \"Main\"!" % (name))
        if not all(isinstance(item, str) for item in data["dependencies"]):
            raise TypeError("An item of key \"dependencies\" of NormalizerFunction \"%s\" is not a str!" % (name))

        self.name = name
        self.dependencies = data["dependencies"]
        self.function_name = data["function_name"]

        self.final:Normalizer.Normalizer|None = None
        self.links_to_other_intermediates:list[Intermediate.Intermediate] = []
        self.parents:list[Intermediate.Intermediate] = []

        self.children_has_normalizer = True

    def set(self, intermediate_comparers: dict[str, Intermediate.Intermediate], functions: dict[str, Callable]) -> None:
        if self.function_name not in functions:
            raise KeyError("Function \"%s\", referenced in key \"function_name\" of NormalizerFunction \"%s\", does not exist!" % (self.function_name, self.name))
        self.final = Normalizer.Normalizer(functions[self.function_name], self.dependencies)
