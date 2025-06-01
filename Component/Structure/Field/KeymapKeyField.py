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


class KeymapKeyField(FieldContainer.FieldContainer[Field.Field]):

    __slots__ = (
        "allow_inline",
        "delegate_arguments",
        "excluded_from_similarity",
        "key",
        "required",
        "similarity_weight",
        "source_component",
        "subcomponent_field",
        "tags_field",
        "tags_for_all_field",
        "types_field",
        "value_weight",
    )

    def __init__(self, data:ComponentTyping.KeymapStructureKeyTypedDict, key:str, tag_set:set["StructureTagComponent.StructureTagComponent"], path:tuple[str,...], source_component:"Component.Component", *, allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed) -> None:
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
        self.delegate_arguments = data.get("delegate_arguments", {})
        self.required = data.get("required", False)
        self.similarity_weight = data.get("similarity_weight", 1)
        self.value_weight = data.get("weight", None)

        self.subcomponent_field = ComponentField.OptionalComponentField(data.get("structure", None), StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("structure",), allow_inline=allow_inline)
        self.tags_field:TagListField.TagListField = TagListField.TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(tag_set)
        self.types_field = TypeListField.TypeListField(data["types"] if isinstance(data["types"], list) else (data["types"]), ("types",)).verify_with(self.subcomponent_field)

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

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.key} id {id(self)}>"
