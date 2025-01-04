from itertools import starmap
from typing import Callable, Iterator

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Utilities.Exceptions as Exceptions


class LinkedObjectsField[a:Component.Component](Field.Field):
    '''A link to multiple other Components.'''


    def __init__(self, subcomponents_data:dict[str,str|ComponentTyping.ComponentTypedDicts], pattern:Pattern.Pattern[a], path:list[str|int], *, allow_inline:Field.InlinePermissions=Field.InlinePermissions.reference, assume_type:str|None=None) -> None:
        '''
        :subcomponents_data: The names of the reference Components and/or data of the inline Components this Field refers to.
        :pattern: The Pattern used to search for Components.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        :assume_type: String to use as the type of an inline Component if the type key is missing from it.
        '''
        super().__init__(path)
        self.subcomponents_data = subcomponents_data
        self.subcomponents:dict[str,a]|None = None
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
        self.subcomponents = {}
        inline_components:list[a] = []
        for key, subcomponent_data in self.subcomponents_data.items():
            subcomponent, is_inline = Field.choose_component(subcomponent_data, source_component, self.pattern, components, imported_components, self.error_path, create_component_function, self.assume_type)
            self.has_reference_components = self.has_reference_components or not is_inline
            self.has_inline_components = self.has_inline_components or is_inline
            self.subcomponents[key] = subcomponent
            if is_inline:
                inline_components.append(subcomponent)
        return list(self.subcomponents.values()), inline_components

    def check(self, source_component:"Component.Component") -> list[Exception]:
        exceptions:list[Exception] = super().check(source_component)
        if self.has_reference_components and self.allow_inline is Field.InlinePermissions.inline:
            exceptions.append(Exceptions.ReferenceComponentError(source_component, self))
        if self.has_inline_components and self.allow_inline is Field.InlinePermissions.reference:
            exceptions.append(Exceptions.InlineComponentError(source_component, self))
        return exceptions

    def for_each[b](self, function:Callable[[str, a],b]) -> None:
        '''
        Calls the given function on each Component in this Field.
        :function: The function to use.
        '''
        if self.subcomponents is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.for_each, self)
        for key, subcomponent in self.subcomponents.items():
            function(key, subcomponent)

    def map[b](self, function:Callable[[str, a],b]) -> Iterator[tuple[str,b]]:
        '''
        Calls the given function on each Component in this Field, and returns the results in the same order.
        :function: The function to use.
        '''
        if self.subcomponents is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.map, self)
        return zip(self.subcomponents.keys(), starmap(function, self.subcomponents.items()))

    def get_components(self) -> dict[str,a]:
        '''
        Returns the Components that this Field refers to.
        Can only be called after `set_field`.
        '''
        if self.subcomponents is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.get_components, self)
        return self.subcomponents

    def check_coverage[b](self, get_final_function:Callable[[a],b], linked_requirements:dict[str,type[b]], component:"Component.Component") -> Iterator[Exception]:
        linked_objects:dict[str,b] = {key: get_final_function(linked_component) for key, linked_component in self.get_components().items()}
        yield from (
            Exceptions.LinkedComponentMissingError(component, key, linked_type)
            for key, linked_type in linked_requirements.items()
            if key not in linked_objects
        )
        yield from (
            Exceptions.LinkedComponentExtraError(component, key, linked_object)
            for key, linked_object in linked_objects.items()
            if key not in linked_requirements
        )
        yield from (
            Exceptions.LinkedComponentTypeError(component, key, required_type, linked_serializer)
            for key, linked_serializer in linked_objects.items()
            if (required_type := linked_requirements.get(key)) is not None and not isinstance(linked_serializer, required_type)
        )

    def check_coverage_types[b](self, get_final_function:Callable[[a],type[b]], linked_requirements:dict[str,type[b]], component:"Component.Component") -> Iterator[Exception]:
        linked_objects:dict[str,type[b]] = {key: get_final_function(linked_component) for key, linked_component in self.get_components().items()}
        yield from (
            Exceptions.LinkedComponentMissingError(component, key, linked_type)
            for key, linked_type in linked_requirements.items()
            if key not in linked_objects
        )
        yield from (
            Exceptions.LinkedComponentExtraError(component, key, linked_object)
            for key, linked_object in linked_objects.items()
            if key not in linked_requirements
        )
        yield from (
            Exceptions.LinkedComponentTypeError(component, key, required_type, linked_serializer)
            for key, linked_serializer in linked_objects.items()
            if (required_type := linked_requirements.get(key)) is not None and not issubclass(linked_serializer, required_type)
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} len {len(self)} id {id(self)}>"

    def __len__(self) -> int:
        return 0 if self.subcomponents is None else len(self.subcomponents)
