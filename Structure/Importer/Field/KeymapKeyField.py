from typing import TYPE_CHECKING, Union

import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.ComponentListField as ComponentListField
import Structure.Importer.Field.Field as Field
import Structure.Importer.Field.TagListField as TagListField
import Structure.Importer.Field.MetaField as MetaField
import Structure.Importer.Field.OptionalComponentField as OptionalComponentField
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

class KeymapKeyField(MetaField.MetaField[Field.Field]):

    def __init__(self, data:ComponentTyping.KeymapKeyTypedDict, key:str, tag_set:set[str], path:list[str|int]) -> None:
        '''
        :data: A dictionary containing the keys {"type": str|list[str], "subcomponent": str|None, tags:list[str]}
        :key: The key that this Field corresponds to.
        :tag_set: The set of tags to update when `set_field` is called.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        self.key = key
        self.types_field = TypeListField.TypeListField(data["type"] if isinstance(data["type"], list) else [data["type"]], ["keys", key, "type"])
        self.subcomponent_field:OptionalComponentField.OptionalComponentField[Union["StructureComponent.StructureComponent","GroupComponent.GroupComponent"]] = OptionalComponentField.OptionalComponentField(data.get("subcomponent", None), COMPONENT_REQUEST_PROPERTIES, ["keys", key, "subcomponent"])
        self.tags_field:TagListField.TagListField = TagListField.TagListField(data.get("tags", []), ["keys", key, "tags"])
        self.types_field.verify_with(self.subcomponent_field)
        self.tags_field.add_to_tag_set(tag_set)
        fields:list[Field.Field] = [self.types_field, self.subcomponent_field, self.tags_field]
        super().__init__(fields, path)

    def add_tag_fields(self, tag_fields:ComponentListField.ComponentListField["TagComponent.TagComponent"]) -> None:
        '''
        Adds some additional ComponentFields of TagComponents to this Field.
        :tag_fields: The list of ComponentFields to add.
        '''
        self.tags_field.extend(tag_fields.get_components())

    def get_subcomponent_final(self) -> dict[tuple[str,type],Union["Structure.Structure",None]]:
        subcomponent = self.subcomponent_field.get_component()
        if subcomponent is None:
            return {(self.key, keymap_type): None for keymap_type in self.types_field.get_types()}
        else:
            keymap_types = self.types_field.get_types()
            structure = subcomponent.final
            assert subcomponent.final is not None
            if isinstance(structure, dict):
                return {(self.key, structure_type): substructure for structure_type, substructure in structure.items()}
            else:
                return {(self.key, keymap_type): structure for keymap_type in keymap_types}

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

    def __repr__(self) -> str:
        return "<%s %s id %i>" % (self.__class__.__name__, self.key, id(self))