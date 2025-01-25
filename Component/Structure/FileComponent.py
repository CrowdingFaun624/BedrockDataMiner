from typing import Sequence

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Structure.Field.DelegateField as DelegateField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.NormalizerComponent as NormalizerComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.FileStructure as FileStructure
import Utilities.TypeVerifier as TypeVerifier


class FileComponent(StructureComponent.StructureComponent[FileStructure.FileStructure]):

    class_name = "File"
    my_capabilities = Capabilities.Capabilities(is_structure=True)
    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("content_types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate", False, (str, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypeVerifier.TypedDictKeyTypeVerifier("file_types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("garbage_collect", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_ancestor_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("max_similarity_descendent_depth", False, (int, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", False, TypeVerifier.UnionTypeVerifier(str, dict, TypeVerifier.ListTypeVerifier((str, dict), list))),
        TypeVerifier.TypedDictKeyTypeVerifier("pre_normalized_types", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("subcomponent", True, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "content_types_field",
        "delegate_field",
        "file_types_field",
        "max_similarity_ancestor_depth",
        "max_similarity_descendent_depth",
        "normalizer_field",
        "post_normalizer_field",
        "pre_normalized_types_field",
        "subcomponent_field",
    )

    def initialize_fields(self, data: ComponentTyping.FileTypedDict) -> Sequence[Field.Field]:
        self.variable_bools["children_has_garbage_collection"] = data.get("garbage_collect", False)
        self.max_similarity_descendent_depth = data.get("max_similarity_descendent_depth", 4)
        self.max_similarity_ancestor_depth = data.get("max_similarity_ancestor_depth", None)

        self.subcomponent_field = ComponentField.OptionalComponentField(data["subcomponent"], StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("subcomponent",))
        self.file_types_field = TypeListField.TypeListField(data.get("file_types", "abstract_file"), ("file_types",)).must_be(self.domain.type_stuff.file_types).add_to_set(self.my_type)
        self.content_types_field = TypeListField.TypeListField(data["content_types"], ("content_types",)).verify_with(self.subcomponent_field)
        self.delegate_field = DelegateField.OptionalDelegateField(data.get("delegate", None), data.get("delegate_arguments", {}), self.domain, ("delegate",))
        self.normalizer_field = ComponentListField.ComponentListField(data.get("normalizer", ()), NormalizerComponent.NORMALIZER_PATTERN, ("normalizer",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.post_normalizer_field = ComponentListField.ComponentListField(data.get("post_normalizer", ()), NormalizerComponent.NORMALIZER_PATTERN, ("post_normalizer",), assume_type=NormalizerComponent.NormalizerComponent.class_name)
        self.pre_normalized_types_field = TypeListField.TypeListField(data.get("pre_normalized_types", ()), ("pre_normalized_types",))
        return (self.subcomponent_field, self.file_types_field, self.content_types_field, self.delegate_field, self.normalizer_field, self.post_normalizer_field, self.pre_normalized_types_field, self.file_types_field)

    def create_final(self) -> FileStructure.FileStructure:
        return FileStructure.FileStructure(
            name=self.name,
            max_similarity_descendent_depth=self.max_similarity_descendent_depth,
            max_similarity_ancestor_depth=self.max_similarity_ancestor_depth,
            children_has_normalizer=self.variable_bools["children_has_normalizer"],
            children_has_garbage_collection=self.variable_bools["children_has_garbage_collection"],
        )

    def link_finals(self) -> list[Exception]:
        exceptions = super().link_finals()
        self.final.link_substructures(
            structure=self.subcomponent_field.map(lambda subcomponent: subcomponent.final),
            delegate=self.delegate_field.create_delegate(self.final, None, exceptions),
            file_types=self.file_types_field.types,
            content_types=self.content_types_field.types,
            normalizer=tuple(self.normalizer_field.map(lambda subcomponent: subcomponent.final)),
            post_normalizer=tuple(self.post_normalizer_field.map(lambda subcomponent: subcomponent.final)),
            pre_normalized_types=self.pre_normalized_types_field.types if len(self.pre_normalized_types_field.types) != 0 else self.file_types_field.types,
            children_tags={tag.final for tag in self.children_tags},
        )
        return exceptions
