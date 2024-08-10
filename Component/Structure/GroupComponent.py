import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.FieldListField as FieldListField
import Component.Structure.Field.GroupItemField as GroupItemField
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.GroupStructure as GroupStructure
import Structure.Structure as Structure
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class GroupComponent(StructureComponent.StructureComponent[GroupStructure.GroupStructure]):

    class_name_article = "a Group"
    class_name = "Group"
    my_capabilities = Capabilities.Capabilities(is_group=True, is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponents", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, (str, dict, type(None)), "a dict", "a str", "a str, StructureComponent, or None")),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    def __init__(self, data:ComponentTyping.GroupTypedDict, name:str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.subcomponents_field = FieldListField.FieldListField([
            GroupItemField.GroupItemField(type_str, subcomponent_str, ["subcomponents", index])
            for index, (type_str, subcomponent_str) in enumerate(data["subcomponents"].items())], ["subcomponents"]
        )
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", None), data.get("delegate_arguments", {}), ["delegate"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.post_normalizer_field = NormalizerListField.NormalizerListField(data.get("post_normalizer", []), ["post_normalizer"])
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        self.fields.extend([self.subcomponents_field, self.delegate_field, self.normalizer_field, self.pre_normalized_types_field, self.post_normalizer_field])

    def get_subcomponents(self) -> list[Component.Component]:
        return [group_item_component for group_item in self.subcomponents_field if (group_item_component := group_item.get_component()) is not None]

    def create_final(self) -> None:
        super().create_final()
        self.final = GroupStructure.GroupStructure(
            name=self.name,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def link_finals(self) -> None:
        super().link_finals()
        substructures:dict[type,Structure.Structure|None] = {}
        all_types:set[type] = set()
        for group_field in self.subcomponents_field:
            valid_types = group_field.get_types()
            all_types.update(valid_types)
            substructures.update((valid_type, group_field.subcomponent_field.get_final()) for valid_type in valid_types)
        self.my_type = all_types
        self.get_final().link_substructures(
            substructures=substructures,
            delegate=self.delegate_field.create_delegate(self.get_final()),
            types=tuple(self.my_type),
            normalizer=self.normalizer_field.get_finals(),
            post_normalizer=self.post_normalizer_field.get_finals(),
            pre_normalized_types=self.pre_normalized_types_field.get_types() if len(self.pre_normalized_types_field.get_types()) != 0 else tuple(all_types),
        )
