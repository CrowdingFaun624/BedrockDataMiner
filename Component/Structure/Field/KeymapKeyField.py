from typing import TYPE_CHECKING, Union, overload

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.FieldContainer as FieldContainer
import Component.Structure.Field.OptionalStructroidComponentField as OptionalStructroidComponentField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.Field.TypeListField as TypeListField
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Structure as Structure

class KeymapKeyField(FieldContainer.FieldContainer[Field.Field]):

    @overload
    def __init__(self, *, key:str, has_been_imported:bool, types_field:TypeListField.TypeListField, subcomponent_field:OptionalStructroidComponentField.OptionalStructroidComponentField, tags_field:TagListField.TagListField, path:list[str|int], allow_inline:Field.InLinePermissions) -> None:
        '''
        This overload is used to copy a KeymapKeyField.
        '''
        ...
    @overload
    def __init__(self, *, data:ComponentTyping.KeymapKeyTypedDict, key:str, tag_set:set[str], path:list[str|int], allow_inline:Field.InLinePermissions=Field.InLinePermissions.mixed) -> None:
        '''
        :data: A dictionary containing the keys {"type": str|list[str], "subcomponent": str|ComponentTyping.StructroidComponentTypedDicts|None, tags:list[str]}
        :key: The key that this Field corresponds to.
        :tag_set: The set of tags to update when `set_field` is called.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        :allow_inline: An InLinePermissions object describing the type of subcomponent_data allowed.
        '''
        ...
    def __init__(
            self,
            *,
            data:ComponentTyping.KeymapKeyTypedDict|None=None,
            key:str|None=None,
            tag_set:set[str]|None=None,
            path:list[str|int]|None=None,
            allow_inline:Field.InLinePermissions=Field.InLinePermissions.mixed,
            has_been_imported:bool|None=None,
            types_field:TypeListField.TypeListField|None=None,
            subcomponent_field:OptionalStructroidComponentField.OptionalStructroidComponentField|None=None,
            tags_field:TagListField.TagListField|None=None,
        ) -> None:
        if data is None:
            if key is None or has_been_imported is None or types_field is None or subcomponent_field is None or tags_field is None or path is None:
                raise Exceptions.InvalidStateError()
            super().__init__([], path)
            self.key = key
            self.has_been_imported = has_been_imported
            self.types_field = types_field
            self.subcomponent_field = subcomponent_field
            self.tags_field = tags_field
            self.allow_inline = allow_inline
        else:
            if path is None or key is None or tag_set is None:
                raise Exceptions.InvalidStateError()
            super().__init__([], path)
            self.key = key
            self.has_been_imported = False # Keys that have been imported cannot be imported again

            self.types_field = TypeListField.TypeListField(data["type"] if isinstance(data["type"], list) else [data["type"]], ["keys", key, "type"])
            self.subcomponent_field = OptionalStructroidComponentField.OptionalStructroidComponentField(data.get("subcomponent", None), ["keys", key, "subcomponent"], allow_inline=allow_inline)
            self.tags_field:TagListField.TagListField = TagListField.TagListField(data.get("tags", []), ["keys", key, "tags"])
            self.tags_field.add_to_tag_set(tag_set)
            self.allow_inline = allow_inline
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

    def get_subcomponent_final(self) -> dict[type,Union["Structure.Structure",None]]:
        '''Extracts the data about the structure of this field's components without changing the identity of the data structures.'''
        structure = self.subcomponent_field.get_final()
        if isinstance(structure, dict):
            return structure
        else:
            return {value_type: structure for value_type in self.types_field.get_types()}

    def copy_for_importing(self) -> "KeymapKeyField":
        return KeymapKeyField(
            key=self.key,
            has_been_imported=True,
            types_field=self.types_field,
            subcomponent_field=self.subcomponent_field,
            tags_field=self.tags_field,
            path=self.error_path,
            allow_inline=self.allow_inline
        )

    def __repr__(self) -> str:
        return "<%s %s id %i>" % (self.__class__.__name__, self.key, id(self))