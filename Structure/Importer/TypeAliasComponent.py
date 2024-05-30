import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Utilities.TypeVerifier as TypeVerifier


class TypeAliasComponent(Component.Component):

    class_name_article = "a TypeAlias"
    class_name = "TypeAlias"
    my_properties = ComponentCapabilities.Capabilities(is_type_alias=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.TypeAliasTypedDict, name:str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)
        if name in ComponentTyping.DEFAULT_TYPES:
            raise ValueError("A TypeAlias's name cannot be one of [%s]!" % ", ".join(ComponentTyping.DEFAULT_TYPES.keys()))

        self.types_strs = data["types"]
        self.types:list[type]|None = None

    def create_final(self) -> None:
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
