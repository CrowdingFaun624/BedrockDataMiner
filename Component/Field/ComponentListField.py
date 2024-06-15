from typing import Callable, Generic, Iterator, Sequence, TypeVar, cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Utilities.Exceptions as Exceptions

a = TypeVar("a", bound=Component.Component, covariant=True)

class ComponentListField(Field.Field, Generic[a]):
    '''A link to multiple other Components.'''

    def __init__(self, subcomponents_data:Sequence[str|ComponentTyping.ComponentTypedDicts]|str|ComponentTyping.ComponentTypedDicts, pattern:Pattern.Pattern[a], path:list[str|int], *, allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed, assume_type:str|None=None) -> None:
        '''
        :subcomponents_data: The names of the reference Components and/or data of the inline Components this Field refers to.
        :pattern: The Pattern used to search for Components.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        :assume_type: String to use as the type of an inline Component if the type key is missing from it.
        '''
        super().__init__(path)
        self.subcomponents_data = cast(Sequence[str|ComponentTyping.ComponentTypedDicts], [subcomponents_data]) if isinstance(subcomponents_data, (str, dict)) else subcomponents_data
        self.subcomponents:list[a]|None = None
        self.pattern = pattern
        self.allow_inline = allow_inline
        self.has_reference_components = False
        self.has_inline_components = False
        self.assume_type = assume_type

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list[a],list[a]]:
        self.subcomponents = []
        inline_components:list[a] = []
        for subcomponent_data in self.subcomponents_data:
            subcomponent, is_inline = Field.choose_component(subcomponent_data, source_component, self.pattern, components, imported_components, self.error_path, create_component_function, self.assume_type)
            self.has_reference_components = self.has_reference_components or not is_inline
            self.has_inline_components = self.has_inline_components or is_inline
            self.subcomponents.append(subcomponent)
            if is_inline:
                inline_components.append(subcomponent)
        return self.subcomponents, inline_components

    def check(self, source_component:"Component.Component") -> list[Exception]:
        exceptions:list[Exception] = super().check(source_component)
        if self.has_reference_components and self.allow_inline is Field.InlinePermissions.inline:
            exceptions.append(Exceptions.ReferenceComponentError(source_component, self))
        if self.has_inline_components and self.allow_inline is Field.InlinePermissions.reference:
            exceptions.append(Exceptions.InlineComponentError(source_component, self))
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
