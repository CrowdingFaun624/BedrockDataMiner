from typing import Self

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Field.FieldContainer as FieldContainer
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Component.Structure.StructureComponent as StructureComponent
import Component.Structure.StructureTagComponent as StructureTagComponent
import Utilities.TypeUtilities as TypeUtilities


class KeymapKeyField(FieldContainer.FieldContainer[Field.Field]):

    __slots__ = (
        "allow_inline",
        "delegate_arguments",
        "key",
        "max_similarity_descendent_depth",
        "required",
        "source_component",
        "subcomponent_field",
        "tags_field",
        "tags_for_all_field",
        "types_field",
        "weight",
    )

    def __init__(self, data:ComponentTyping.KeymapKeyTypedDict, key:str, tag_set:set["StructureTagComponent.StructureTagComponent"], path:tuple[str,...], source_component:"Component.Component", *, allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed) -> None:
        '''
        :data: A dictionary containing the keys data.
        :key: The key that this Field corresponds to.
        :tag_set: The set of tags to update when `set_field` is called.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :source_component: The original Component that owns this Field.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__([], path)
        self.key = key
        self.source_component = source_component # used to make sure keys cannot be imported in chains.
        self.allow_inline = allow_inline
        self.weight = data.get("weight", 1)
        self.delegate_arguments = data.get("delegate_arguments", {})
        self.required = data.get("required", False)
        self.max_similarity_descendent_depth = data.get("max_similarity_descendent_depth", ...)

        self.subcomponent_field = ComponentField.OptionalComponentField(data.get("subcomponent", None), StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("keys", key, "subcomponent"), allow_inline=allow_inline)
        self.types_field = TypeListField.TypeListField(data["types"] if isinstance(data["types"], list) else (data["types"]), ("keys", key, "types",)).verify_with(self.subcomponent_field)
        self.tags_field:TagListField.TagListField = TagListField.TagListField(data.get("tags", ()), ("keys", key, "tags")).add_to_tag_set(tag_set)
        self.tags_for_all_field:TagListField.TagListField|None = None

        self.fields.extend((self.types_field, self.subcomponent_field, self.tags_field))

    def add_tag_fields(self, tag_fields:TagListField.TagListField) -> Self:
        '''
        Makes this KeymapKeyField extend its own tags_field when `set_field` is called.
        :tag_fields: The list of ComponentFields to add from.
        '''
        self.tags_field.import_from(tag_fields)
        return self

    def add_to_tag_set(self, tag_set:set["StructureTagComponent.StructureTagComponent"]) -> None:
        '''
        Makes this KeymapKeyField add its tags (in string form) to the given tag set.
        :tag_set: The set of strings to add to.
        '''
        self.tags_field.add_to_tag_set(tag_set)

    def conditional_must_be(self, condition:bool, types:TypeUtilities.TypeSet, *, fail_message:str|None=None) -> Self:
        if condition:
            self.types_field.must_be(types, fail_message=fail_message)
        return self

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.key} id {id(self)}>"
