from typing import Callable, Generic, Sequence, TypeVar

import Structure.Importer.Component as Component
import Structure.Importer.Field.Field as Field
import Structure.Importer.Pattern as Capabilities
import Utilities.Exceptions as Exceptions

a = TypeVar("a", bound=Component.Component, covariant=True)

class OptionalComponentField(Field.Field, Generic[a]):
    '''A link to another Component.'''

    def __init__(self, subcomponent_str:str|None, pattern:Capabilities.Pattern[a], path:list[str|int]) -> None:
        '''
        :subcomponent_str: The name of the Component this Field refers to.
        :pattern: The Pattern used to search for Components.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.subcomponent_str = subcomponent_str
        self.subcomponent:a|None = None
        self.pattern = pattern
        self.has_set_component = False

    def set_field(self, component_name:str, component_class_name:str, components:dict[str,Component.Component], imported_components:dict[str,dict[str,Component.Component]], functions:dict[str,Callable]) -> Sequence[Component.Component]:
        self.has_set_component = True
        if self.subcomponent_str is None:
            self.subcomponent = None
            return []
        else:
            self.subcomponent = Field.choose_component(self.subcomponent_str, self.pattern, components, imported_components, self.error_path, component_name, component_class_name)
            return [self.subcomponent]

    def get_component(self) -> a|None:
        '''
        Returns the Component that this Field refers to.
        Can only be called after `set_field`.
        '''
        if not self.has_set_component:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.get_component, self)
        return self.subcomponent
