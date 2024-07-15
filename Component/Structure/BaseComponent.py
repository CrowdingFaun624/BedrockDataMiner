import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.StructureComponentField as StructureComponentField
import Structure.StructureBase as StructureBase
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class BaseComponent(Component.Component[StructureBase.StructureBase]):

    class_name_article = "a Base"
    class_name = "Base"
    my_capabilities = Capabilities.Capabilities(is_base=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("imports", "a list", False, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("components", "a dict", True, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
                TypeVerifier.TypedDictKeyTypeVerifier("as", "a str", False, str),
                TypeVerifier.TypedDictKeyTypeVerifier("component", "a str", True, str),
            ), list, "a dict", "a list")),
            TypeVerifier.TypedDictKeyTypeVerifier("from", "a str", True, str),
        ), list, "a dict", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or StructureComponent", True, (str, dict)),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    def __init__(self, data:ComponentTyping.BaseTypedDict, name:str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.structure_name = data["name"]
        self.imports = data.get("imports", None)

        self.subcomponent_field = StructureComponentField.StructureComponentField(data["subcomponent"], ["subcomponent"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.post_normalizer_field = NormalizerListField.NormalizerListField(data.get("post_normalizer", []), ["post_normalizer"])
        self.fields.extend([self.subcomponent_field, self.normalizer_field, self.post_normalizer_field])

    def create_final(self) -> None:
        super().create_final()
        self.final = StructureBase.StructureBase(
            component_name=self.name,
            structure_name=self.structure_name,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        super().link_finals()
        self.get_final().link_substructures(
            structure=self.subcomponent_field.get_final(),
            normalizer=self.normalizer_field.get_finals(),
            post_normalizer=self.post_normalizer_field.get_finals(),
        )
