from typing import Callable

import Comparison.ComparerImporter.ComparerTyping as ComparerTyping
import Comparison.ComparerImporter.Intermediate as Intermediate

class TypeAliasIntermediate(Intermediate.Intermediate):

    def __init__(self, data:ComparerTyping.TypeAliasTypedDict, name:str, index:int) -> None:
        self.check_types(data, name, index, [
            ("type", str, "a str", True),
            ("types", list, "a list", True),
        ])
        if data["type"] != "TypeAlias":
            raise ValueError("Key \"type\" of TypeAlias \"%s\" is not \"TypeAlias\"!" % (name))
        if name in ("dict", "float", "int", "list", "str"):
            raise ValueError("TypeAlias \"%s\" has an invalid name!" % name)

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
                raise KeyError("Duplicate type \"%s\" of TypeAlias \"%s\"." % (type_str, self.name))
            already_types.add(type_str)
            if type_str in ComparerTyping.DEFAULT_TYPES:
                self.types.append(ComparerTyping.DEFAULT_TYPES[type_str])
            else:
                raise KeyError("TypeAlias refers to type \"%s\", which is not a valid default type!" % type_str)
