import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.StructureComponent as StructureComponent
import Component.Structure.StructureTagComponent as StructureTagComponent
import Structure.StructureBase as StructureBase
import Utilities.TypeVerifier as TypeVerifier

STRUCTURE_BASE_PATTERN:Pattern.Pattern["BaseComponent"] = Pattern.Pattern("is_base")

class BaseComponent(Component.Component[StructureBase.StructureBase]):

    class_name = "Base"
    my_capabilities = Capabilities.Capabilities(is_base=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("default_delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("default_delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", True, (str, dict)),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
    )

    __slots__ = (
        "children_tags",
        "default_delegate_field",
        "delegate_field",
        "normalizer_field",
        "post_normalizer_field",
        "pre_normalized_types_field",
        "subcomponent_field",
        "types_field",
    )

    def initialize_fields(self, data: ComponentTyping.BaseTypedDict) -> list[Field.Field]:
        self.subcomponent_field = ComponentField.ComponentField(data["subcomponent"], StructureComponent.STRUCTURE_COMPONENT_PATTERN, ["subcomponent"])
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", "DefaultBaseDelegate"), data.get("delegate_arguments", {}), self.domain, ["delegate"])
        self.default_delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("default_delegate", "DefaultDelegate"), data.get("default_delegate_arguments", {}), self.domain, ["default_delegate"])
        self.normalizer_field = ComponentListField.ComponentListField(data.get("normalizer", []), NormalizerComponent.NORMALIZER_PATTERN, ["normalizer"], assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.post_normalizer_field = ComponentListField.ComponentListField(data.get("post_normalizer", []), NormalizerComponent.NORMALIZER_PATTERN, ["post_normalizer"], assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"]).verify_with(self.subcomponent_field)
        return [self.subcomponent_field, self.delegate_field, self.default_delegate_field, self.normalizer_field, self.post_normalizer_field, self.pre_normalized_types_field, self.types_field]

    def get_propagated_variables(self) -> tuple[dict[str, bool], dict[str, set]]:
        self.children_tags:set[StructureTagComponent.StructureTagComponent] = set()
        return {"children_has_garbage_collection": False}, {"children_tags": self.children_tags}

    def create_final(self) -> StructureBase.StructureBase:
        return StructureBase.StructureBase(
            name=self.component_group,
            domain=self.domain,
            children_has_garbage_collection=self.variable_bools["children_has_garbage_collection"],
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_substructures(
            structure=self.subcomponent_field.subcomponent.final,
            types=self.types_field.types,
            pre_normalized_types=self.pre_normalized_types_field.types if len(self.pre_normalized_types_field.types) != 0 else self.types_field.types,
            delegate=self.delegate_field.create_delegate(self.final, exceptions=exceptions),
            default_delegate=self.default_delegate_field.create_delegate(None, exceptions=exceptions),
            normalizer=list(self.normalizer_field.map(lambda subcomponent: subcomponent.final)),
            post_normalizer=list(self.post_normalizer_field.map(lambda subcomponent: subcomponent.final)),
            children_tags={tag.final for tag in self.children_tags},
        )
        return exceptions

    def finalize(self) -> list[Exception]:
        exceptions = super().finalize()
        self.final.finalize()
        return exceptions
