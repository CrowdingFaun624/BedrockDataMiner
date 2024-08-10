from typing import TYPE_CHECKING, Union

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.FieldContainer as FieldContainer
import Component.Structure.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField

if TYPE_CHECKING:
    import Component.Component as Component
    import Structure.Structure as Structure

class KeymapKeyField(FieldContainer.FieldContainer[Field.Field]):

    def __init__(self, data:ComponentTyping.KeymapKeyTypedDict, key:str, tag_set:set[str], path:list[str|int], source_component:"Component.Component", *, allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed) -> None:
        '''
        :data: A dictionary containing the keys {"type": str|list[str], "subcomponent": str|ComponentTyping.StructureComponentTypedDicts|None, tags:list[str]}
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

        self.types_field = TypeListField.TypeListField(data["type"] if isinstance(data["type"], list) else [data["type"]], ["keys", key, "type"])
        self.subcomponent_field = OptionalStructureComponentField.OptionalStructureComponentField(data.get("subcomponent", None), ["keys", key, "subcomponent"], allow_inline=allow_inline)
        self.tags_field:TagListField.TagListField = TagListField.TagListField(data.get("tags", []), ["keys", key, "tags"])
        self.tags_field.add_to_tag_set(tag_set)
        self.types_field.verify_with(self.subcomponent_field)
        self.tags_for_all_field:TagListField.TagListField|None = None

        self.fields.extend([self.types_field, self.subcomponent_field, self.tags_field])

    def add_tag_fields(self, tag_fields:TagListField.TagListField) -> None:
        '''
        Makes this KeymapKeyField extend its own tags_field when `set_field` is called.
        :tag_fields: The list of ComponentFields to add from.
        '''
        self.tags_field.import_from(tag_fields)

    def add_to_tag_set(self, tag_set:set[str]) -> None:
        '''
        Makes this KeymapKeyField add its tags (in string form) to the given tag set.
        :tag_set: The set of strings to add to.
        '''
        self.tags_field.add_to_tag_set(tag_set)

    def get_types(self) -> tuple[type,...]:
        '''Return the list of types that this key can be.'''
        return self.types_field.get_types()

    def get_subcomponent(self) -> Union["Structure.Structure", None]:
        '''Return the Structure that this KeymapKeyField refers to.'''
        return self.subcomponent_field.get_final()

    def __repr__(self) -> str:
        return "<%s %s id %i>" % (self.__class__.__name__, self.key, id(self))
