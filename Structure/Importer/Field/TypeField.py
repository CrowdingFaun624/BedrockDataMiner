from typing import TYPE_CHECKING, Callable, Sequence

import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.AbstractTypeField as AbstractTypeField
import Structure.Importer.Field.Field as Field
import Structure.Importer.Pattern as Capabilities
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Importer.Component as Component
    import Structure.Importer.TypeAliasComponent as TypeAliasComponent

TYPE_ALIAS_REQUEST_PROPERTIES:Capabilities.Pattern["TypeAliasComponent.TypeAliasComponent"] = Capabilities.Pattern([{"is_type_alias": True}])

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
            component = Field.choose_component(self.subcomponent_str, TYPE_ALIAS_REQUEST_PROPERTIES, components, self.error_path, component_name, component_class_name)
            self.subcomponent = component
            return [component]

    def resolve(self) -> None:
        if self.subcomponent is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.resolve, self)
        if isinstance(self.subcomponent, type):
            self.types = [self.subcomponent]
        else:
            self.types = self.subcomponent.get_types()

    def get_types(self) -> list[type]:
        if self.types is None:
            raise Exceptions.FieldSequenceBreakError(self.resolve, self.get_types, self)
        return self.types
