import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Structure.Field.NormalizerListField as NormalizerListField
import Component.Structure.Field.OptionalDelegateField as OptionalDelegateField
import Component.Structure.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Component.Types as Types
import Structure.FileStructure as FileStructure
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier


class FileComponent(StructureComponent.StructureComponent[FileStructure.FileStructure]):

    class_name_article = "a File"
    class_name = "File"
    my_capabilities = Capabilities.Capabilities(is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("content_types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a list or str", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", "a str or null", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", "a dict", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("file_types", "a str or list", True, TypeVerifier.UnionTypeVerifier("a list or str", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("garbage_collect", "a bool", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_ancestor_depth", "an int or None", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_descendent_depth", "an int or None", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a str, NormalizerComponent, or list", False, TypeVerifier.UnionTypeVerifier("a str, NormalizerComponent, or list", str, dict, TypeVerifier.ListTypeVerifier((str, dict), list, "a str or NormalizerComponent", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", "a str or list", False, TypeVerifier.UnionTypeVerifier("a str or list", str, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list"))),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", "a str, StructureComponent or None", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", "a str", False, str),
    )

    __slots__ = (
        "content_types_field",
        "delegate_field",
        "file_types_field",
        "max_similarity_ancestor_depth",
        "max_similarity_descendent_depth",
        "my_type",
        "normalizer_field",
        "post_normalizer_field",
        "pre_normalized_types_field",
        "subcomponent_field",
    )

    def initialize_fields(self, data: ComponentTyping.FileTypedDict) -> list[Field.Field]:
        self.children_has_garbage_collection = data.get("garbage_collect", False)
        self.max_similarity_descendent_depth = data.get("max_similarity_descendent_depth", 4)
        self.max_similarity_ancestor_depth = data.get("max_similarity_ancestor_depth", None)

        self.subcomponent_field = OptionalStructureComponentField.OptionalStructureComponentField(data["subcomponent"], ["subcomponent"])
        self.file_types_field = TypeListField.TypeListField(data.get("file_types", "abstract_file"), ["file_types"])
        self.content_types_field = TypeListField.TypeListField(data["content_types"], ["content_types"])
        self.delegate_field = OptionalDelegateField.OptionalDelegateField(data.get("delegate", None), data.get("delegate_arguments", {}), ["delegate"])
        self.normalizer_field = NormalizerListField.NormalizerListField(data.get("normalizer", []), ["normalizer"])
        self.post_normalizer_field = NormalizerListField.NormalizerListField(data.get("post_normalizer", []), ["post_normalizer"])
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", []), ["pre_normalized_types"])
        self.content_types_field.verify_with(self.subcomponent_field)
        self.file_types_field.must_be(Types.file_types)
        return [self.subcomponent_field, self.file_types_field, self.content_types_field, self.delegate_field, self.normalizer_field, self.post_normalizer_field, self.pre_normalized_types_field, self.file_types_field]

    def create_final(self) -> None:
        super().create_final()
        self.final = FileStructure.FileStructure(
            name=self.name,
            max_similarity_descendent_depth=self.max_similarity_descendent_depth,
            max_similarity_ancestor_depth=self.max_similarity_ancestor_depth,
            children_has_normalizer=self.children_has_normalizer,
            children_has_garbage_collection=self.children_has_garbage_collection,
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.get_final().link_substructures(
            structure=self.subcomponent_field.get_final(),
            delegate=self.delegate_field.create_delegate(self.get_final(), None, exceptions),
            file_types=self.file_types_field.get_types(),
            content_types=self.content_types_field.get_types(),
            normalizer=self.normalizer_field.get_finals(),
            post_normalizer=self.post_normalizer_field.get_finals(),
            pre_normalized_types=self.pre_normalized_types_field.get_types() if len(self.pre_normalized_types_field.get_types()) != 0 else self.file_types_field.get_types(),
            children_tags={tag.get_final() for tag in self.children_tags},
        )
        self.my_type = set(self.file_types_field.get_types())
        return exceptions
