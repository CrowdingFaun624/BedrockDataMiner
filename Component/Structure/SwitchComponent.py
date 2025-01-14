import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Component.Structure.Field.NormalizerField as NormalizerField
import Component.Structure.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Structure.SwitchStructure as SwitchStructure
import Utilities.TypeVerifier as TypeVerifier


class SwitchComponent(StructureComponent.StructureComponent[SwitchStructure.SwitchStructure]):
    
    class_name = "Switch"
    class_name_article = "a Switch"
    my_capabilities = Capabilities.Capabilities(is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_ancestor_depth", "an int or None", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_descendent_depth", "an int or None", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponents", "a dict", True, TypeVerifier.DictTypeVerifier(dict, str, (str, dict, type(None)), "a dict", "a str", "a str, StructureComponent, or None")),
        TypeVerifier.TypedDictKeyTypeVerifier("switch_function", "a str or NormalizerComponent", True, (str, dict)),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
        TypeVerifier.TypedDictKeyTypeVerifier("types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
    )

    def initialize_fields(self, data:ComponentTyping.SwitchTypedDict) -> list[Field.Field]:
        self.max_similarity_descendent_depth = data.get("max_similarity_descendent_depth", 4)
        self.max_similarity_ancestor_depth = data.get("max_similarity_ancestor_depth", None)

        self.subcomponents_field = {key: OptionalStructureComponentField.OptionalStructureComponentField(subdata, ["subcomponents", key]) for key, subdata in data["subcomponents"].items()}
        self.switch_function_field = NormalizerField.NormalizerField(data["switch_function"], ["switch_function"])
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", None), data.get("delegate_arguments", {}), self.domain, ["delegate"])
        self.types_field = TypeListField.TypeListField(data["types"], ["types"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.post_normalizer_field = NormalizerListField.NormalizerListField(data.get("post_normalizer", []), ["post_normalizer"])
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
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
            switch_function=self.switch_function_field.final,
            switches={key: field.final for key, field in self.subcomponents_field.items()},
            delegate=self.delegate_field.create_delegate(self.final, exceptions=exceptions),
            types=self.types_field.types,
            normalizer=self.normalizer_field.finals,
            post_normalizer=self.post_normalizer_field.finals,
            pre_normalized_types=self.pre_normalized_types_field.types if len(self.pre_normalized_types_field.types) != 0 else self.types_field.types,
            children_tags={tag.final for tag in self.children_tags},
        )
        self.my_type = set(self.types_field.types)
        return exceptions
