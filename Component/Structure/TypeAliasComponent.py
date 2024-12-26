import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Types as Types
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class TypeAliasComponent(Component.Component[tuple[type,...]]):

    class_name_article = "a TypeAlias"
    class_name = "TypeAlias"
    my_capabilities = Capabilities.Capabilities(is_type_alias=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.TypeAliasTypedDict, name:str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)

        if name in Types.default_types:
            raise Exceptions.ComponentInvalidNameError(self, list(Types.default_types.keys()))

        self.types_strs = data["types"]

    def create_final(self) -> None:
        super().create_final()
        final:list[type] = []
        already_types:set[str] = set()
        for type_str in self.types_strs:
            if type_str in already_types:
                raise Exceptions.ComponentDuplicateTypeError(type_str, self)
            already_types.add(type_str)
            if type_str in Types.default_types:
                final.append(Types.default_types[type_str])
            else:
                raise Exceptions.ComponentUnrecognizedTypeError(type_str, self)
        self.final = tuple(final)
