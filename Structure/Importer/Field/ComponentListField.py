from typing import Callable, Generic, Iterator, Sequence, TypeVar

import Structure.Importer.Component as Component
import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.Field.Field as Field

a = TypeVar("a", bound=Component.Component, covariant=True)

class ComponentListField(Field.Field, Generic[a]):
    '''A link to multiple other Components.'''

    def __init__(self, subcomponents_strs:list[str], capabilities_pattern:ComponentCapabilities.CapabilitiesPattern, path:list[str|int]) -> None:
        '''
        :subcomponents_strs: The names of the Components this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.subcomponents_strs = subcomponents_strs
        self.subcomponents:list[a]|None = None
        self.capabilities_pattern = capabilities_pattern

    def set_field(self, component_name:str, component_class_name:str, components:dict[str,"Component.Component"], functions:dict[str,Callable]) -> Sequence["Component.Component"]:
        self.subcomponents = []
        for subcomponent_str in self.subcomponents_strs:
            subcomponent = Field.choose_component(subcomponent_str, self.capabilities_pattern, components, self.error_path, component_name, component_class_name)
            assert subcomponent is not None
            self.subcomponents.append(subcomponent) # type: ignore
        return self.subcomponents

    def extend(self, new_components:Sequence[a]) -> None:
        '''
        Adds new components to this Field.
        :new_components: The sequence of Components to add.
        '''
        if self.subcomponents is None:
            raise RuntimeError("Cannot call `extend` before `set`!")
        self.subcomponents.extend(new_components)

    b = TypeVar("b")

    def for_each(self, function:Callable[[a],b]) -> None:
        '''
        Calls the given function on each Component in this Field.
        :function: The function to use.
        '''
        if self.subcomponents is None:
            raise RuntimeError("Cannot call `for_each` before `set`!")
        for subcomponent in self.subcomponents:
            function(subcomponent)

    def map(self, function:Callable[[a],b]) -> Iterator[b]:
        '''
        Calls the given function on each Component in this Field, and returns the results in the same order.
        :function: The function to use.
        '''
        if self.subcomponents is None:
            raise RuntimeError("Cannot call `map` before `set`!")
        return (function(subcomponent) for subcomponent in self.subcomponents)

    def get_components(self) -> list[a]:
        '''
        Returns the Components that this Field refers to.
        Can only be called after `set`.
        '''
        if self.subcomponents is None:
            raise RuntimeError("Cannot call `get_components` before `set`!")
        return self.subcomponents # type: ignore

    def __repr__(self) -> str:
        return "<%s len %i id %i>" % (self.__class__.__name__, len(self), id(self))

    def __len__(self) -> int:
        if self.subcomponents is None: return 0
        return len(self.subcomponents)
