from typing import TYPE_CHECKING, Callable, Sequence

import Structure.Importer.Field.AbstractTypeField as AbstractTypeField
import Structure.Importer.Field.Field as Field
import Structure.Importer.Pattern as Capabilities
import Structure.Importer.StructureComponent as StructureComponent
import Structure.Importer.TypeAliasComponent as TypeAliasComponent
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Importer.Component as Component

TYPE_ALIAS_REQUEST_PROPERTIES:Capabilities.Pattern[TypeAliasComponent.TypeAliasComponent] = Capabilities.Pattern([{"is_type_alias": True}])

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
                raise Exceptions.ComponentDuplicateTypeError(subcomponent_str, self, "(referenced in %sof %s \"%s\")" % (Field.get_keys_strs(False, self.error_path), component_class_name, component_name))
            already_types.add(subcomponent_str)
            if subcomponent_str in StructureComponent.DEFAULT_TYPES:
                subcomponent_type = StructureComponent.DEFAULT_TYPES[subcomponent_str]
                self.primitive_types.append(subcomponent_type)
            else:
                subcomponent = Field.choose_component(subcomponent_str, TYPE_ALIAS_REQUEST_PROPERTIES, components, self.error_path, component_name, component_class_name)
                components_used.append(subcomponent)
                self.type_aliases.append(subcomponent)
        return components_used

    def resolve(self) -> None:
        if self.primitive_types is None or self.type_aliases is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.resolve, self)
        self.types = []
        self.types.extend(self.primitive_types)
        for type_alias_component in self.type_aliases:
            self.types.extend(type_alias_component.get_final())

    def get_types(self) -> list[type]:
        if self.types is None:
            raise Exceptions.FieldSequenceBreakError(self.resolve, self.get_types, self)
        return self.types
