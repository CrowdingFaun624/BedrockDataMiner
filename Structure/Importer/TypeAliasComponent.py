from typing import Callable

import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Utilities.TypeVerifier as TypeVerifier

class TypeAliasComponent(Component.Component):

    class_name_article = "a TypeAlias"
    class_name = "TypeAlias"

    my_properties = ComponentCapabilities.Capabilities(is_type_alias=True)

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("data", "a dict", True, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, TypeVerifier.EnumTypeVerifier((class_name,))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
        )),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str, lambda key, value: (value not in ComponentTyping.DEFAULT_TYPES, "\"name\" cannot be one of [%s]!" % ", ".join(ComponentTyping.DEFAULT_TYPES.keys()))),
        TypeVerifier.TypedDictKeyTypeVerifier("index", "an int", True, int),
    )

    def __init__(self, data:ComponentTyping.TypeAliasTypedDict, name:str, index:int) -> None:
        self.type_verifier.base_verify({"data": data, "name": name, "index": index}, ["%s \"%s\"" % (self.class_name, name)])

        self.name = name
        self.types_strs = data["types"]

        self.types:list[type]|None = None
        self.links_to_other_components:list[Component.Component] = []
        self.parents:list[Component.Component] = []

        self.children_has_normalizer = False

    def set(self, components:dict[str,Component.Component], functions:dict[str,Callable]) -> None:
        self.types = []
        already_types:set[str] = set()
        for type_str in self.types_strs:
            if type_str in already_types:
                raise KeyError("Duplicate type \"%s\" of %s \"%s\"." % (type_str, self.class_name, self.name))
            already_types.add(type_str)
            if type_str in ComponentTyping.DEFAULT_TYPES:
                self.types.append(ComponentTyping.DEFAULT_TYPES[type_str])
            else:
                raise KeyError("%s \"%s\" refers to type \"%s\", which is not a valid default type!" % (self.class_name, self.name, type_str))
