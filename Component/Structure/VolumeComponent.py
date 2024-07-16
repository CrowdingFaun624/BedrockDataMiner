import Component.Capabilities as Capabilities
import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeField as TypeField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Structure.GroupStructure as GroupStructure
import Structure.VolumeStructure as VolumeStructure
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class VolumeComponent(StructureComponent.StructureComponent[GroupStructure.GroupStructure]):

    class_name_article = "a Volume"
    class_name = "Volume"
    my_capabilities = Capabilities.Capabilities(is_group=True, is_structure=True)
    children_has_normalizer_default = True
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("field", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("position_key", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("print_additional_data", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("state_key", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str, StructureComponent or None", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("tags", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("this_type", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def __init__(self, data:ComponentTyping.VolumeTypedDict, name: str, component_group:str, index:int|None) -> None:
        super().__init__(data, name, component_group, index)
        self.verify_arguments(data)

        self.field = data.get("field", "block")
        self.position_key = data["position_key"]
        self.print_additional_data = data.get("print_additional_data", True)
        self.state_key = data["state_key"]
        self.children_has_normalizer = True # has to turn into tuple that the thing recognizes.
        self.final_structure:VolumeStructure.VolumeStructure|None=None

        self.subcomponent_field = OptionalStructureComponentField.OptionalStructureComponentField(data.get("subcomponent"), ["subcomponent"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.post_normalizer_field = NormalizerListField.NormalizerListField(data.get("post_normalizer", []), ["post_normalizer"])
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.this_type_field = TypeListField.TypeListField(data.get("this_type", "list"), ["this_type"])
        self.tags_field = TagListField.TagListField(data.get("tags", []), ["tags"])
        self.types_field.verify_with(self.subcomponent_field)
        self.tags_field.add_to_tag_set(self.children_tags)
        self.this_type_field.must_be(StructureComponent.ARBITRARY_ITERABLE_TYPES)
        self.fields.extend([self.subcomponent_field, self.normalizer_field, self.types_field, self.this_type_field, self.tags_field, self.pre_normalized_types_field, self.post_normalizer_field])

    def get_subcomponents(self) -> list[Component.Component]:
        subcomponent = self.subcomponent_field.get_component()
        return [] if subcomponent is None else [subcomponent]

    def create_final(self) -> None:
        super().create_final()
        self.final = GroupStructure.GroupStructure(
            name=self.name + ".volume_group",
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )
        self.final_structure = VolumeStructure.VolumeStructure(
            name=self.name,
            field=self.field,
            position_key=self.position_key,
            state_key=self.state_key,
            print_additional_data=self.print_additional_data,
            children_has_normalizer=self.children_has_normalizer,
            children_tags=self.children_tags,
        )

    def get_final_structure(self) -> VolumeStructure.VolumeStructure:
        if self.final_structure is None:
            raise Exceptions.AttributeNoneError("final_structure", self)
        return self.final_structure

    def link_finals(self) -> None:
        super().link_finals()
        final_structure = self.get_final_structure()
        this_type = self.this_type_field.get_types()
        self.my_type = set(this_type)
        self.my_type.add(tuple)
        final_structure.link_substructures(
            types=self.types_field.get_types(),
            structure=self.subcomponent_field.get_final(),
            normalizer=self.normalizer_field.get_finals(),
            post_normalizer=self.post_normalizer_field.get_finals(),
            pre_normalized_types=(tuple,),
            tags=self.tags_field.get_finals(),
        )
        self.get_final().link_substructures(
            substructures={my_type: final_structure for my_type in self.my_type},
            types=tuple(self.my_type),
            normalizer=[],
            post_normalizer=[],
            pre_normalized_types=self.pre_normalized_types_field.get_types() if len(self.pre_normalized_types_field.get_types()) != 0 else this_type,
        )
