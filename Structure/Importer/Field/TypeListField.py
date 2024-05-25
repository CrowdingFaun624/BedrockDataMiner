from typing import TYPE_CHECKING, Callable, Sequence

import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.Field as Field
import Structure.Importer.TypeAliasComponent as TypeAliasComponent

if TYPE_CHECKING:
    import Structure.Importer.Component as Component

TYPE_ALIAS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class TypeListField(Field.Field):
    '''A link to multiple TypeAliasComponents and/or types.'''

    def __init__(self, subcomponents_strs:list[str], path:list[str|int]) -> None:
        '''
        :subcomponents_strs: List of string representing a default type or Component.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.subcomponents_strs = subcomponents_strs
        self.types:list[type]|None = None

    def set(self, component_name:str, component_class_name:str, components:dict[str,"Component.Component"], functions:dict[str,Callable]) -> Sequence["Component.Component"]:
        components_used:list["Component.Component"] = []
        self.types = []
        already_types:set[str] = set()
        for subcomponent_str in self.subcomponents_strs:
            if subcomponent_str in already_types:
                raise KeyError("Duplicate type \"%s\" of %sof %s \"%s\"." % (subcomponent_str, Field.get_keys_strs(False, self.error_path), component_class_name, component_name))
            already_types.add(subcomponent_str)
            if subcomponent_str in ComponentTyping.DEFAULT_TYPES:
                subcomponent_type = ComponentTyping.DEFAULT_TYPES[subcomponent_str]
                self.types.append(subcomponent_type)
            else:
                subcomponent = Field.choose_component(subcomponent_str, TYPE_ALIAS_REQUEST_PROPERTIES, components, self.error_path, component_name, component_class_name, TypeAliasComponent.TypeAliasComponent)
                components_used.append(subcomponent)
                self.types.extend(subcomponent.types)
        return components_used

    def get_types(self) -> list[type]:
        '''
        Returns a list of types that this TypeField references.
        Can only be called after `set`.
        '''
        if self.types is None:
            raise RuntimeError("Cannot call `get_types` before `set`!")
        return self.types
