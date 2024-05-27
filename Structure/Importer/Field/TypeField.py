from typing import TYPE_CHECKING, Callable, Sequence

import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.AbstractTypeField as AbstractTypeField
import Structure.Importer.Field.Field as Field
import Structure.Importer.TypeAliasComponent as TypeAliasComponent

if TYPE_CHECKING:
    import Structure.Importer.Component as Component

TYPE_ALIAS_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_type_alias": True}])

class TypeField(AbstractTypeField.AbstractTypeField):
    '''A link to a TypeAliasComponent or type.'''

    def __init__(self, subcomponent_str:str, path:list[str|int]) -> None:
        '''
        :subcomponent_str: String representing a default type or Component.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.subcomponent_str = subcomponent_str
        self.subcomponent:type|TypeAliasComponent.TypeAliasComponent|None = None
        self.types:list[type]|None = None

    def set_field(self, component_name:str, component_class_name:str, components:dict[str,"Component.Component"], functions:dict[str,Callable]) -> Sequence["Component.Component"]:
        if self.subcomponent_str in ComponentTyping.DEFAULT_TYPES:
            self.subcomponent = ComponentTyping.DEFAULT_TYPES[self.subcomponent_str]
            return []
        else:
            self.subcomponent = Field.choose_component(self.subcomponent_str, TYPE_ALIAS_REQUEST_PROPERTIES, components, self.error_path, component_name, component_class_name, TypeAliasComponent.TypeAliasComponent)
            assert self.subcomponent is not None and not isinstance(self.subcomponent, type)
            return [self.subcomponent]

    def resolve(self) -> None:
        if self.subcomponent is None:
            raise RuntimeError("Cannot call `resolve` before `set_field`!")
        if isinstance(self.subcomponent, type):
            self.types = [self.subcomponent]
        else:
            assert self.subcomponent.types is not None
            self.types = self.subcomponent.types

    def get_types(self) -> list[type]:
        if self.types is None:
            raise RuntimeError("Cannot call `get_types` before `resolve`!")
        return self.types
