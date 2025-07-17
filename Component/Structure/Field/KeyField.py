from typing import Self

from Component.ComponentTyping import KeyTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field
from Component.Field.FieldContainer import FieldContainer
from Component.Structure.Field.AbstractTypeField import AbstractTypeField
from Component.Structure.Field.TagListField import TagListField
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.StructureComponent import (
    STRUCTURE_COMPONENT_PATTERN,
    StructureComponent,
)
from Component.Structure.StructureTagComponent import StructureTagComponent
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class KeyField(FieldContainer[Field]):

    # not used by any Field class, but just put here so both KeymapStructureComponent and SwitchStructureComponent can both grab it.
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
        TypedDictKeyTypeVerifier("required", False, bool),
        TypedDictKeyTypeVerifier("similarity_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
        TypedDictKeyTypeVerifier("structure", False, (str, dict, type(None))),
        TypedDictKeyTypeVerifier("tags", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("types", True, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("value_weight", False, (int, type(None)), lambda key, value: (value is None or value >= 0, "must be positive")),
    )

    __slots__ = (
        "delegate_arguments",
        "excluded_from_similarity",
        "key",
        "required",
        "similarity_weight",
        "source_component",
        "structure_field",
        "tags_field",
        "tags_for_all_field",
        "types_field",
        "value_weight",
    )

    def __init__(
        self,
        data:KeyTypedDict,
        key:str,
        tag_set:set["StructureTagComponent"],
        source_component:"StructureComponent",
        path:tuple[str,...],
        cumulative_path:tuple[str,...]|None=None,
    ) -> None:
        '''
        :data: A dictionary containing the keys data.
        :key: The key that this Field corresponds to.
        :tag_set: The set of tags to update when `set_field` is called.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        :source_component: The original Component that owns this Field.
        '''
        super().__init__([], path, cumulative_path)
        if cumulative_path is None: cumulative_path = path
        self.key = key
        self.source_component = source_component # used to make sure keys cannot be imported in chains.
        self.delegate_arguments = data.get("delegate_arguments", {})
        self.required = data.get("required", False)
        self.similarity_weight = data.get("similarity_weight", 1)
        self.value_weight = data.get("weight", None)

        self.structure_field = OptionalComponentField(data.get("structure", None), STRUCTURE_COMPONENT_PATTERN, ("structure",), (*cumulative_path, "structure"))
        self.tags_field = TagListField(data.get("tags", ()), ("tags",), (*cumulative_path, "tags")).add_to_tag_set(tag_set)
        self.types_field = TypeListField(data["types"] if isinstance(data["types"], list) else (data["types"]), ("types",), (*cumulative_path, "types")).verify_with(self.structure_field)

        self.tags_for_all_field:TagListField|None = None

        self.fields.extend((self.types_field, self.structure_field, self.tags_field))

    def add_tag_fields(self, tag_fields:TagListField) -> Self:
        '''
        Makes this KeyField extend its own tags_field when `set_field` is called.
        :tag_fields: The list of ComponentFields to add from.
        '''
        self.tags_field.import_from(tag_fields)
        return self

    def add_to_tag_set(self, tag_set:set["StructureTagComponent"]) -> None:
        '''
        Makes this KeyField add its tags (in string form) to the given tag set.
        :tag_set: The set of strings to add to.
        '''
        self.tags_field.add_to_tag_set(tag_set)

    def make_default(self, type_field:"AbstractTypeField") -> Self:
        self.types_field.make_default(type_field)
        return self

    def add_to_type_set(self, type_set:set[type]) -> Self:
        self.types_field.add_to_set(type_set)
        return self

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.key} id {id(self)}>"
