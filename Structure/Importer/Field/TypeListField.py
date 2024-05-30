from typing import TYPE_CHECKING, Callable, Sequence, TypeAlias, Union

import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.AbstractTypeField as AbstractTypeField
import Structure.Importer.Field.ComponentField as ComponentField
import Structure.Importer.Field.Field as Field
import Structure.Importer.Field.OptionalComponentField as OptionalComponentField
import Structure.Importer.TypeAliasComponent as TypeAliasComponent

if TYPE_CHECKING:
    import Structure.Importer.Component as Component
    import Structure.Importer.GroupComponent as GroupComponent
    import Structure.Importer.StructureComponent as StructureComponent

TYPE_ALIAS_REQUEST_PROPERTIES:ComponentCapabilities.CapabilitiesPattern[TypeAliasComponent.TypeAliasComponent] = ComponentCapabilities.CapabilitiesPattern([{"is_type_alias": True}])
VerifyComponentType:TypeAlias = ComponentField.ComponentField[Union["StructureComponent.StructureComponent", "GroupComponent.GroupComponent"]]|OptionalComponentField.OptionalComponentField[Union["StructureComponent.StructureComponent", "GroupComponent.GroupComponent"]]

class TypeListField(AbstractTypeField.AbstractTypeField):
    '''A link to multiple TypeAliasComponents and/or types.'''

    def __init__(self, subcomponents_strs:list[str]|str, path:list[str|int]) -> None:
        '''
        :subcomponents_strs: List of string representing a default type or Component.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.subcomponents_strs = [subcomponents_strs] if isinstance(subcomponents_strs, str) else subcomponents_strs
        self.primitive_types:list[type]|None = None
        self.type_aliases:list[TypeAliasComponent.TypeAliasComponent]|None = None
        self.types:list[type]|None = None

    def set_field(self, component_name:str, component_class_name:str, components:dict[str,"Component.Component"], functions:dict[str,Callable]) -> Sequence["Component.Component"]:
        components_used:list["Component.Component"] = []
        self.primitive_types = []
        self.type_aliases = []
        already_types:set[str] = set()
        for subcomponent_str in self.subcomponents_strs:
            if subcomponent_str in already_types:
                raise KeyError("Duplicate type \"%s\" of %sof %s \"%s\"." % (subcomponent_str, Field.get_keys_strs(False, self.error_path), component_class_name, component_name))
            already_types.add(subcomponent_str)
            if subcomponent_str in ComponentTyping.DEFAULT_TYPES:
                subcomponent_type = ComponentTyping.DEFAULT_TYPES[subcomponent_str]
                self.primitive_types.append(subcomponent_type)
            else:
                subcomponent = Field.choose_component(subcomponent_str, TYPE_ALIAS_REQUEST_PROPERTIES, components, self.error_path, component_name, component_class_name)
                components_used.append(subcomponent)
                self.type_aliases.append(subcomponent)
        return components_used

    def resolve(self) -> None:
        if self.primitive_types is None:
            raise RuntimeError("Cannot call `resolve` before `set_field`!")
        assert self.type_aliases is not None
        self.types = []
        self.types.extend(self.primitive_types)
        for type_alias_component in self.type_aliases:
            if type_alias_component.types is None:
                raise RuntimeError("Cannot call `resolve` before all TypeAliases are set!")
            self.types.extend(type_alias_component.types)

    def get_types(self) -> list[type]:
        if self.types is None:
            raise RuntimeError("Cannot call `get_types` before `resolve`!")
        return self.types
