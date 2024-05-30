from typing import TYPE_CHECKING, Union, overload

import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.ComponentListField as ComponentListField
import Structure.Importer.Field.Field as Field
import Structure.Importer.Field.FieldContainer as FieldContainer
import Structure.Importer.Field.OptionalComponentField as OptionalComponentField
import Structure.Importer.Field.TagListField as TagListField
import Structure.Importer.Field.TypeListField as TypeListField
from Structure.Importer.ImporterConfig import ImporterConfig

if TYPE_CHECKING:
    import Structure.Importer.GroupComponent as GroupComponent
    import Structure.Importer.StructureComponent as StructureComponent
    import Structure.Importer.TagComponent as TagComponent
    import Structure.Structure as Structure

COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_group": True}, {"is_structure": True}])
IMPORTABLE_KEYS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"has_importable_keys": True}])
NORMALIZER_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_normalizer": True}])

class KeymapKeyField(FieldContainer.FieldContainer[Field.Field]):

    @overload
    def __init__(self, *, key:str, has_been_imported:bool, types_field:TypeListField.TypeListField, subcomponent_field:OptionalComponentField.OptionalComponentField[Union["StructureComponent.StructureComponent","GroupComponent.GroupComponent"]], tags_field:TagListField.TagListField, path:list[str|int]) -> None:
        '''
        This overload is used to copy a KeymapKeyField.
        '''
        ...
    @overload
    def __init__(self, *, data:ComponentTyping.KeymapKeyTypedDict, key:str, tag_set:set[str], path:list[str|int]) -> None:
        '''
        :data: A dictionary containing the keys {"type": str|list[str], "subcomponent": str|None, tags:list[str]}
        :key: The key that this Field corresponds to.
        :tag_set: The set of tags to update when `set_field` is called.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        ...
    def __init__(
            self,
            *,
            data:ComponentTyping.KeymapKeyTypedDict|None=None,
            key:str|None=None,
            tag_set:set[str]|None=None,
            path:list[str|int]|None=None,
            has_been_imported:bool|None=None,
            types_field:TypeListField.TypeListField|None=None,
            subcomponent_field:OptionalComponentField.OptionalComponentField[Union["StructureComponent.StructureComponent","GroupComponent.GroupComponent"]]|None=None,
            tags_field:TagListField.TagListField|None=None,
        ) -> None:
        if data is None:
            assert key is not None
            assert has_been_imported is not None
            assert types_field is not None
            assert subcomponent_field is not None
            assert tags_field is not None
            assert path is not None
            super().__init__([], path)
            self.key = key
            self.has_been_imported = has_been_imported
            self.types_field = types_field
            self.subcomponent_field = subcomponent_field
            self.tags_field = tags_field
        else:
            assert path is not None
            assert key is not None
            assert tag_set is not None
            super().__init__([], path)
            self.key = key
            self.has_been_imported = False # Keys that have been imported cannot be imported again

            self.types_field = TypeListField.TypeListField(data["type"] if isinstance(data["type"], list) else [data["type"]], ["keys", key, "type"])
            self.subcomponent_field:OptionalComponentField.OptionalComponentField[Union["StructureComponent.StructureComponent","GroupComponent.GroupComponent"]] = OptionalComponentField.OptionalComponentField(data.get("subcomponent", None), COMPONENT_REQUEST_PROPERTIES, ["keys", key, "subcomponent"])
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

    def get_subcomponent_final(self) -> dict[type,Union["Structure.Structure",None]]:
        '''Extracts the data about the structure of this field's components without changing the identity of the data structures.'''
        subcomponent = self.subcomponent_field.get_component()
        value_types = self.types_field.get_types()
        if subcomponent is None:
            return {value_type: None for value_type in value_types}
        else:
            assert subcomponent.final is not None
            if isinstance(subcomponent.final, dict):
                return subcomponent.final
            else:
                return {value_type: subcomponent.final for value_type in value_types}

    def check(self, component_name:str, component_class_name:str, config: ImporterConfig) -> list[Exception]:
        exceptions = super().check(component_name, component_class_name, config)
        subcomponent = self.subcomponent_field.get_component()
        key_types = self.types_field.get_types()
        if subcomponent is None:
            for key_type in key_types:
                if key_type in ComponentTyping.REQUIRES_SUBCOMPONENT_TYPES:
                    exceptions.append(TypeError("Key \"%s\" of %s \"%s\" accepts type %s, but has a null Subcomponent!" % (self.key, component_class_name, component_name, key_type.__name__)))
        else:
            if set(key_types) != set(subcomponent.my_type):
                my_types = ", ".join(type_item.__name__ for type_item in sorted(key_types, key=lambda x: x.__name__))
                its_types = ", ".join(type_item.__name__ for type_item in sorted(subcomponent.my_type, key=lambda x: x.__name__))
                exceptions.append(TypeError("Key \"%s\" of %s \"%s\" accepts types [%s], but its Subcomponent, \"%s\", only accepts type [%s]!" % (self.key, component_class_name, component_name, my_types, subcomponent.name, its_types)))
        return exceptions

    def copy_for_importing(self) -> "KeymapKeyField":
        return KeymapKeyField(
            key=self.key,
            has_been_imported=True,
            types_field=self.types_field,
            subcomponent_field=self.subcomponent_field,
            tags_field=self.tags_field,
            path=self.error_path,
        )

    def __repr__(self) -> str:
        return "<%s %s id %i>" % (self.__class__.__name__, self.key, id(self))