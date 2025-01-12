import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier as TypeVerifier


class TypeAliasComponent(Component.Component[tuple[type,...]]):

    class_name_article = "a TypeAlias"
    class_name = "TypeAlias"
    my_capabilities = Capabilities.Capabilities(is_type_alias=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a list", True, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
    )

    __slots__ = (
        "types_strs",
    )

    def initialize_fields(self, data: ComponentTyping.TypeAliasTypedDict) -> list[Field.Field]:
        if self.name in self.domain.type_stuff.default_types:
            raise Exceptions.ComponentInvalidNameError(self, list(self.domain.type_stuff.default_types.keys()))
        self.types_strs = data["types"]
        return []

    def create_final(self) -> tuple[type,...]:
        final:list[type] = []
        already_types:set[str] = set()
        default_types = self.domain.type_stuff.default_types
        for type_str in self.types_strs:
            if type_str in already_types:
                raise Exceptions.ComponentDuplicateTypeError(type_str, self)
            already_types.add(type_str)
            if type_str in default_types:
                final.append(default_types[type_str])
            else:
                raise Exceptions.ComponentUnrecognizedTypeError(type_str, self)
        return tuple(final)
