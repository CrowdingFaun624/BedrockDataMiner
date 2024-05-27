from typing import Callable, Generic, Sequence, TypeVar, Union

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.Field.Field as Field

a = TypeVar("a", bound=Component.Component, covariant=True)

class ComponentField(Field.Field, Generic[a]):
    '''A link to another Component.'''

    def __init__(self, subcomponent_str:str, capabilities_pattern:ComponentCapabilities.CapabilitiesPattern, path:list[str|int]) -> None:
        '''
        :subcomponent_str: The name of the Component this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.subcomponent_str = subcomponent_str
        self.subcomponent:Union[a,None] = None
        self.capabilities_pattern = capabilities_pattern
    
    def set_field(self, component_name:str, component_class_name:str, components:dict[str,Component.Component], functions:dict[str,Callable]) -> Sequence[Component.Component]:
        subcomponent:"Component.Component" = Field.choose_component(self.subcomponent_str, self.capabilities_pattern, components, self.error_path, component_name, component_class_name)
        self.subcomponent = subcomponent # type: ignore
        assert self.subcomponent is not None
        return [self.subcomponent]

    def get_component(self) -> a:
        '''
        Returns the Component that this Field refers to.
        Can only be called after `set`.
        '''
        if self.subcomponent is None:
            raise RuntimeError("Cannot call `get_component` before `set`!")
        return self.subcomponent # type: ignore
