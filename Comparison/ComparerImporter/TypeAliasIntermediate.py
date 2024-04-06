from typing import Callable

import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.Intermediate as Intermediate
import Comparison.ComparerImporter.IntermediateCapabilities as IntermediateCapabilities
import Utilities.TypeVerifier as TypeVerifier

class TypeAliasIntermediate(Intermediate.Intermediate):

    class_name_article = "a TypeAlias"
    class_name = "TypeAlias"

    my_properties = IntermediateCapabilities.Capabilities(is_type_alias=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str, lambda key, value: (value not in ComparerTyping.DEFAULT_TYPES, "\"name\" cannot be one of [%s]!" % ", ".join(ComparerTyping.DEFAULT_TYPES.keys()))),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int),
    )

    def __init__(self, data:ComparerTyping.TypeAliasTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.types_strs = data["types"]

        self.types:list[type]|None = None
        self.links_to_other_intermediates:list[Intermediate.Intermediate] = []
        self.parents:list[Intermediate.Intermediate] = []

        self.children_has_normalizer = False

    def set(self, intermediate_comparers:dict[str,Intermediate.Intermediate], functions:dict[str,Callable]) -> None:
        self.types = []
        already_types:set[str] = set()
        for type_str in self.types_strs:
            if type_str in already_types:
                raise KeyError("Duplicate type \"%s\" of %s \"%s\"." % (type_str, self.class_name, self.name))
            already_types.add(type_str)
            if type_str in ComparerTyping.DEFAULT_TYPES:
                self.types.append(ComparerTyping.DEFAULT_TYPES[type_str])
            else:
                raise KeyError("%s \"%s\" refers to type \"%s\", which is not a valid default type!" % (self.class_name, self.name, type_str))
