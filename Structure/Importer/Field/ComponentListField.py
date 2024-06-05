from typing import Callable, Generic, Iterator, Sequence, TypeVar

import Structure.Importer.Component as Component
import Structure.Importer.Field.Field as Field
import Structure.Importer.Pattern as Capabilities
import Utilities.Exceptions as Exceptions

a = TypeVar("a", bound=Component.Component, covariant=True)

class ComponentListField(Field.Field, Generic[a]):
    '''A link to multiple other Components.'''

    def __init__(self, subcomponents_strs:list[str]|str, pattern:Capabilities.Pattern[a], path:list[str|int]) -> None:
        '''
        :subcomponents_strs: The names of the Components this Field refers to.
        :pattern: The Pattern used to search for Components.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.subcomponents_strs = [subcomponents_strs] if isinstance(subcomponents_strs, str) else subcomponents_strs
        self.subcomponents:list[a]|None = None
        self.pattern = pattern

    def set_field(self, component_name:str, component_class_name:str, components:dict[str,"Component.Component"], functions:dict[str,Callable]) -> Sequence["Component.Component"]:
        self.subcomponents = []
        for subcomponent_str in self.subcomponents_strs:
            self.subcomponents.append(Field.choose_component(subcomponent_str, self.pattern, components, self.error_path, component_name, component_class_name))
        return self.subcomponents

    def extend(self, new_components:Sequence[a]) -> None:
        '''
        Adds new components to this Field.
        :new_components: The sequence of Components to add.
        '''
        if self.subcomponents is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.extend, self)
        self.subcomponents.extend(new_components)

    b = TypeVar("b")

    def for_each(self, function:Callable[[a],b]) -> None:
        '''
        Calls the given function on each Component in this Field.
        :function: The function to use.
        '''
        if self.subcomponents is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.for_each, self)
        for subcomponent in self.subcomponents:
            function(subcomponent)

    def map(self, function:Callable[[a],b]) -> Iterator[b]:
        '''
        Calls the given function on each Component in this Field, and returns the results in the same order.
        :function: The function to use.
        '''
        if self.subcomponents is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.map, self)
        return (function(subcomponent) for subcomponent in self.subcomponents)

    def get_components(self) -> list[a]:
        '''
        Returns the Components that this Field refers to.
        Can only be called after `set_field`.
        '''
        if self.subcomponents is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.get_components, self)
        return self.subcomponents # type: ignore

    def __repr__(self) -> str:
        return "<%s len %i id %i>" % (self.__class__.__name__, len(self), id(self))

    def __len__(self) -> int:
        if self.subcomponents is None: return 0
        return len(self.subcomponents)
