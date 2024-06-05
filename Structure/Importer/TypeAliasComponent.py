import Structure.Importer.Capabilities as Capabilities
import Structure.Importer.Component as Component
import Structure.Importer.ComponentTyping as ComponentTyping
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class TypeAliasComponent(Component.Component):

    class_name_article = "a TypeAlias"
    class_name = "TypeAlias"
    my_capabilities = Capabilities.Capabilities(is_type_alias=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.TypeAliasTypedDict, name:str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)
        if name in ComponentTyping.DEFAULT_TYPES:
            raise Exceptions.ComponentInvalidNameError(self, list(ComponentTyping.DEFAULT_TYPES.keys()))

        self.types_strs = data["types"]
        self.types:list[type]|None = None

    def create_final(self) -> None:
        self.types = []
        already_types:set[str] = set()
        for type_str in self.types_strs:
            if type_str in already_types:
                raise Exceptions.ComponentDuplicateTypeError(type_str, self)
            already_types.add(type_str)
            if type_str in ComponentTyping.DEFAULT_TYPES:
                self.types.append(ComponentTyping.DEFAULT_TYPES[type_str])
            else:
                raise Exceptions.ComponentUnrecognizedTypeError(type_str, self)

    def get_types(self) -> list[type]:
        if self.types is None:
            raise Exceptions.AttributeNoneError("types", self)
        return self.types
