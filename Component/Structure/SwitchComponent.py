from typing import Sequence

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.OptionalComponentField as OptionalComponentField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.SwitchStructure as SwitchStructure
import Utilities.TypeVerifier as TypeVerifier


class SwitchComponent(StructureComponent.StructureComponent[SwitchStructure.SwitchStructure]):

    class_name = "Switch"
    my_capabilities = Capabilities.Capabilities(is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_ancestor_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_descendent_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponents", True, TypeVerifier.DictTypeVerifier(dict, str, (str, dict, type(None)))),
        TypeVerifier.TypedDictKeyTypeVerifier("switch_function", True, (str, dict)),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
    )

    __slots__ = (
        "delegate_field",
        "max_similarity_descendent_depth",
        "max_similarity_ancestor_depth",
        "normalizer_field",
        "post_normalizer_field",
        "pre_normalized_types_field",
        "subcomponents_field",
        "switch_function_field",
        "types_field",
    )

    def initialize_fields(self, data:ComponentTyping.SwitchTypedDict) -> Sequence[Field.Field]:
        self.max_similarity_descendent_depth = data.get("max_similarity_descendent_depth", 4)
        self.max_similarity_ancestor_depth = data.get("max_similarity_ancestor_depth", None)

        self.subcomponents_field = {key: OptionalComponentField.OptionalComponentField(subdata, StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("subcomponents", key)) for key, subdata in data["subcomponents"].items()}
        self.switch_function_field = ComponentField.ComponentField(data["switch_function"], NormalizerComponent.NORMALIZER_PATTERN, ("switch_function",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", None), data.get("delegate_arguments", {}), self.domain, ("delegate",))
        self.types_field = TypeListField.TypeListField(data["types"], ("types",)).add_to_set(self.my_type)
        self.normalizer_field = ComponentListField.ComponentListField(data.get("normalizer", ()), NormalizerComponent.NORMALIZER_PATTERN, ("normalizer",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.post_normalizer_field = ComponentListField.ComponentListField(data.get("post_normalizer", ()), NormalizerComponent.NORMALIZER_PATTERN, ("post_normalizer",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", ()), ("pre_normalized_types",))
        # types field is not verified
        fields = [self.switch_function_field, self.delegate_field, self.types_field, self.normalizer_field, self.pre_normalized_types_field, self.post_normalizer_field]
        fields.extend(self.subcomponents_field.values())
        return fields

    def create_final(self) -> SwitchStructure.SwitchStructure:
        return SwitchStructure.SwitchStructure(
            name=self.name,
            max_similarity_ancestor_depth=self.max_similarity_ancestor_depth,
            max_similarity_descendent_depth=self.max_similarity_descendent_depth,
            children_has_normalizer=self.variable_bools["children_has_normalizer"],
            children_has_garbage_collection=self.variable_bools["children_has_garbage_collection"],
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_substructures(
            switch_function=self.switch_function_field.subcomponent.final,
            switches={key: field.get_final(lambda subcomponent: subcomponent.final) for key, field in self.subcomponents_field.items()},
            delegate=self.delegate_field.create_delegate(self.final, exceptions=exceptions),
            types=self.types_field.types,
            normalizer=tuple(self.normalizer_field.map(lambda subcomponent: subcomponent.final)),
            post_normalizer=tuple(self.post_normalizer_field.map(lambda subcomponent: subcomponent.final)),
            pre_normalized_types=self.pre_normalized_types_field.types if len(self.pre_normalized_types_field.types) != 0 else self.types_field.types,
            children_tags={tag.final for tag in self.children_tags},
        )
        return exceptions
