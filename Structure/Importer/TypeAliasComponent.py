import Structure.Importer.Capabilities as Capabilities
import Structure.Importer.Component as Component
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.StructureComponent as StructureComponent
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class TypeAliasComponent(Component.Component[list[type]]):

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
        if name in StructureComponent.DEFAULT_TYPES:
            raise Exceptions.ComponentInvalidNameError(self, list(StructureComponent.DEFAULT_TYPES.keys()))

        self.types_strs = data["types"]

    def create_final(self) -> None:
        self.final = []
        already_types:set[str] = set()
        for type_str in self.types_strs:
            if type_str in already_types:
                raise Exceptions.ComponentDuplicateTypeError(type_str, self)
            already_types.add(type_str)
            if type_str in StructureComponent.DEFAULT_TYPES:
                self.final.append(StructureComponent.DEFAULT_TYPES[type_str])
            else:
                raise Exceptions.ComponentUnrecognizedTypeError(type_str, self)
