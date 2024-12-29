import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.StructureComponentField as StructureComponentField
import Component.Structure.Field.TypeListField as TypeListField
import Structure.StructureBase as StructureBase
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class BaseComponent(Component.Component[StructureBase.StructureBase]):

    class_name_article = "a Base"
    class_name = "Base"
    my_capabilities = Capabilities.Capabilities(is_base=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("default_delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("default_delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("imports", "a list", False, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("components", "a list", True, TypeVerifier.ListTypeVerifier(TypeVerifier.TypedDictTypeVerifier(
                TypeVerifier.TypedDictKeyTypeVerifier("as", "a str", False, str),
                TypeVerifier.TypedDictKeyTypeVerifier("component", "a str", True, str),
            ), list, "a dict", "a list")),
            TypeVerifier.TypedDictKeyTypeVerifier("from", "a str", True, str),
        ), list, "a dict", "a list")),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str or StructureComponent", True, (str, dict)),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    __slots__ = (
        "default_delegate_field",
        "delegate_field",
        "imports",
        "normalizer_field",
        "post_normalizer_field",
        "pre_normalized_types_field",
        "subcomponent_field",
        "types_field",
    )

    def initialize_fields(self, data: ComponentTyping.BaseTypedDict) -> list[Field.Field]:
        self.imports = data.get("imports", None)

        self.subcomponent_field = StructureComponentField.StructureComponentField(data["subcomponent"], ["subcomponent"])
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", "DefaultBaseDelegate"), data.get("delegate_arguments", {}), self.domain, ["delegate"])
        self.default_delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("default_delegate", "DefaultDelegate"), data.get("default_delegate_arguments", {}), self.domain, ["default_delegate"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.post_normalizer_field = NormalizerListField.NormalizerListField(data.get("post_normalizer", []), ["post_normalizer"])
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.types_field.verify_with(self.subcomponent_field)
        return [self.subcomponent_field, self.delegate_field, self.default_delegate_field, self.normalizer_field, self.post_normalizer_field, self.pre_normalized_types_field, self.types_field]

    def create_final(self) -> None:
        super().create_final()
        self.final = StructureBase.StructureBase(
            name=self.component_group,
            domain=self.domain,
            children_has_garbage_collection=self.children_has_garbage_collection,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.get_final().link_substructures(
            structure=self.subcomponent_field.get_final(),
            types=self.types_field.get_types(),
            pre_normalized_types=self.pre_normalized_types_field.get_types() if len(self.pre_normalized_types_field.get_types()) != 0 else self.types_field.get_types(),
            delegate=self.delegate_field.create_delegate(self.get_final(), exceptions=exceptions),
            default_delegate=self.default_delegate_field.create_delegate(None, exceptions=exceptions),
            normalizer=self.normalizer_field.get_finals(),
            post_normalizer=self.post_normalizer_field.get_finals(),
            children_tags={tag.get_final() for tag in self.children_tags},
        )
        return exceptions

    def finalize(self) -> None:
        super().finalize()
        self.get_final().finalize()
