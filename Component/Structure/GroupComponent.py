from itertools import chain

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.OptionalComponentField as OptionalComponentField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.TypeField as TypeField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.GroupStructure as GroupStructure
import Structure.Structure as Structure
import Utilities.TypeVerifier as TypeVerifier


class GroupComponent(StructureComponent.StructureComponent[GroupStructure.GroupStructure]):

    class_name = "Group"
    my_capabilities = Capabilities.Capabilities(is_group=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_ancestor_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_descendent_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponents", True, TypeVerifier.DictTypeVerifier(dict, str, (str, dict, type(None)))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "delegate_field",
        "max_similarity_ancestor_depth",
        "max_similarity_descendent_depth",
        "my_type",
        "normalizer_field",
        "post_normalizer_field",
        "pre_normalized_types_field",
        "subcomponents_field",
    )

    def initialize_fields(self, data: ComponentTyping.GroupTypedDict) -> list[Field.Field]:
        self.max_similarity_descendent_depth = data.get("max_similarity_descendent_depth", 4)
        self.max_similarity_ancestor_depth = data.get("max_similarity_ancestor_depth", None)

        self.subcomponents_field = [
            (
                (subcomponent_field := OptionalComponentField.OptionalComponentField(subcomponent_str, StructureComponent.STRUCTURE_COMPONENT_PATTERN, ["subcomponent", index])),
                TypeField.TypeField(type_str, ["subcomponents", index]).verify_with(subcomponent_field),
            )
            for index, (type_str, subcomponent_str) in enumerate(data["subcomponents"].items())
        ]
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", None), data.get("delegate_arguments", {}), self.domain, ["delegate"])
        self.normalizer_field = ComponentListField.ComponentListField(data.get("normalizer", []), NormalizerComponent.NORMALIZER_PATTERN, ["normalizer"], assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.post_normalizer_field = ComponentListField.ComponentListField(data.get("post_normalizer", []), NormalizerComponent.NORMALIZER_PATTERN, ["post_normalizer"], assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        output:list[Field.Field] = [self.delegate_field, self.normalizer_field, self.pre_normalized_types_field, self.post_normalizer_field]
        output.extend(chain.from_iterable(self.subcomponents_field))
        return output

    def create_final(self) -> GroupStructure.GroupStructure:
        return GroupStructure.GroupStructure(
            name=self.name,
            max_similarity_descendent_depth=self.max_similarity_descendent_depth,
            max_similarity_ancestor_depth=self.max_similarity_ancestor_depth,
            children_has_normalizer=self.variable_bools["children_has_normalizer"],
            children_has_garbage_collection=self.variable_bools["children_has_garbage_collection"],
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        substructures:dict[type,Structure.Structure|None] = {}
        all_types:set[type] = set()
        for (subcomponent_field, type_field) in self.subcomponents_field:
            valid_types = type_field.types
            all_types.update(valid_types)
            substructures.update((valid_type, subcomponent_field.get_final(lambda subcomponent: subcomponent.final)) for valid_type in valid_types)
        self.my_type = all_types
        self.final.link_substructures(
            substructures=substructures,
            delegate=self.delegate_field.create_delegate(self.final, exceptions=exceptions),
            types=tuple(self.my_type),
            normalizer=list(self.normalizer_field.map(lambda subcomponent: subcomponent.final)),
            post_normalizer=list(self.post_normalizer_field.map(lambda subcomponent: subcomponent.final)),
            pre_normalized_types=self.pre_normalized_types_field.types if len(self.pre_normalized_types_field.types) != 0 else tuple(all_types),
            children_tags={tag.final for tag in self.children_tags},
        )
        return exceptions
