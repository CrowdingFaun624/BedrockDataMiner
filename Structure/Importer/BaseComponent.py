import Structure.Importer.Capabilities as Capabilities
import Structure.Importer.Component as Component
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.NormalizerListField as NormalizerListField
import Structure.Importer.Field.StructureComponentField as StructureComponentField
import Structure.StructureBase as StructureBase
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class BaseComponent(Component.Component):

    class_name_article = "a Base"
    class_name = "Base"
    my_capabilities = Capabilities.Capabilities(is_base=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("imports", "a list", False, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("from", "a str", True, str),
            TypeVerifier.TypedDictKeyTypeVerifier("components", "a dict", True, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
                TypeVerifier.TypedDictKeyTypeVerifier("component", "a str", True, str),
                TypeVerifier.TypedDictKeyTypeVerifier("as", "a str", False, str),
            ), list, "a dict", "a list")),
        ), list, "a dict", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", True, str),
    )

    def __init__(self, data:ComponentTyping.BaseComponentTypedDict, name:str) -> None:
        super().__init__(name)
        self.verify_arguments(data, name)

        self.structure_name = data["name"]
        self.imports = data.get("imports", None)
        self.final:StructureBase.StructureBase|None = None

        self.subcomponent_field = StructureComponentField.StructureComponentField(data["subcomponent"], ["subcomponent"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.fields.extend([self.subcomponent_field, self.normalizer_field])

    def create_final(self) -> None:
        self.final = StructureBase.StructureBase(
            component_name=self.name,
            structure_name=self.structure_name,
            children_tags=self.children_tags,
        )

    def get_final(self) -> StructureBase.StructureBase:
        if self.final is None:
            raise Exceptions.AttributeNoneError("final", self)
        return self.final

    def link_finals(self) -> None:
        super().link_finals()
        self.get_final().link_substructures(
            structure=self.subcomponent_field.get_final(),
            normalizer=self.normalizer_field.get_finals(),
        )
