from typing import Callable, Generic, Iterator, Sequence, TypeVar

import Structure.Importer.Component as Component
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.Field as Field
import Structure.Importer.Pattern as Pattern
import Utilities.Exceptions as Exceptions

a = TypeVar("a", bound=Component.Component, covariant=True)

class ComponentListField(Field.Field, Generic[a]):
    '''A link to multiple other Components.'''

    def __init__(self, subcomponents_data:Sequence[str|ComponentTyping.ComponentTypedDicts]|str|ComponentTyping.ComponentTypedDicts, pattern:Pattern.Pattern[a], path:list[str|int], *, allow_in_line:Field.InLinePermissions=Field.InLinePermissions.mixed) -> None:
        '''
        :subcomponents_data: The names of the reference Components and/or data of the in-line Components this Field refers to.
        :pattern: The Pattern used to search for Components.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        :allow_in_line: An InLinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__(path)
        self.subcomponents_data = [subcomponents_data] if isinstance(subcomponents_data, (str, dict)) else subcomponents_data
        self.subcomponents:list[a]|None = None
        self.pattern = pattern
        self.allow_in_line = allow_in_line
        self.has_reference_components = False
        self.has_in_line_components = False

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list[a],list[a]]:
        self.subcomponents = []
        in_line_components:list[a] = []
        for subcomponent_data in self.subcomponents_data:
            subcomponent, is_in_line = Field.choose_component(subcomponent_data, source_component, self.pattern, components, imported_components, self.error_path, create_component_function)
            self.has_reference_components = self.has_reference_components or not is_in_line
            self.has_in_line_components = self.has_in_line_components or is_in_line
            self.subcomponents.append(subcomponent)
            if is_in_line:
                in_line_components.append(subcomponent)
        return self.subcomponents, in_line_components

    def check(self, source_component:"Component.Component") -> list[Exception]:
        exceptions:list[Exception] = super().check(source_component)
        if self.has_reference_components and self.allow_in_line is Field.InLinePermissions.in_line:
            exceptions.append(Exceptions.ReferenceComponentError(source_component, self))
        if self.has_in_line_components and self.allow_in_line is Field.InLinePermissions.reference:
            exceptions.append(Exceptions.InLineComponentError(source_component, self))
        return exceptions

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
