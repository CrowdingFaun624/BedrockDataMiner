from itertools import starmap
from typing import TYPE_CHECKING, Callable, Iterator, Mapping, Sequence

import Utilities.Exceptions as Exceptions
from Component.Component import Component
from Component.ComponentTyping import ComponentTypedDicts, CreateComponentFunction
from Component.Field.Field import Field, InlinePermissions, choose_component
from Component.Pattern import AbstractPattern
from Component.ScriptImporter import ScriptSetSetSet
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

class ComponentDictField[a:Component](Field):
    '''A link to multiple other Components.'''

    __slots__ = (
        "allow_inline",
        "assume_type",
        "has_inline_components",
        "has_reference_components",
        "pattern",
        "subcomponents",
        "subcomponents_data",
    )

    def __init__(
        self,
        subcomponents_data:dict[str,str|ComponentTypedDicts]|dict[str,str]|dict[str,ComponentTypedDicts],
        pattern:AbstractPattern[a],
        path:tuple[str,...],
        cumulative_path:tuple[str,...]|None=None,
        *,
        allow_inline:InlinePermissions=InlinePermissions.mixed,
        assume_type:str|None=None,
    ) -> None:
        '''
        :subcomponents_data: The names of the reference Components and/or data of the inline Components this Field refers to.
        :pattern: The Pattern used to search for Components.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        :assume_type: String to use as the type of an inline Component if the type key is missing from it.
        '''
        super().__init__(path, cumulative_path)
        self.subcomponents_data = subcomponents_data
        self.subcomponents:dict[str,a]
        self.pattern = pattern
        self.allow_inline = allow_inline
        self.has_reference_components = False
        self.has_inline_components = False
        self.assume_type = assume_type

    def set_field(
        self,
        source_component:"Component",
        local_group:"Group",
        global_groups:Mapping[str,Mapping[str,"Group"]],
        functions:"ScriptSetSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence[a],Sequence[a]]:
        with trace.enter_keys(self.trace_path, self.subcomponents_data):
            self.subcomponents = {}
            inline_components:list[a] = []
            for key, subcomponent_data in self.subcomponents_data.items():
                with trace.enter_key(key, subcomponent_data):
                    subcomponent, is_inline = choose_component(subcomponent_data, source_component, self.pattern, local_group, global_groups, trace, self.cumulative_path, functions, create_component_function, self.assume_type)
                    self.has_reference_components = self.has_reference_components or not is_inline
                    self.has_inline_components = self.has_inline_components or is_inline
                    if subcomponent is ...:
                        continue
                    self.subcomponents[key] = subcomponent
                    if is_inline:
                        inline_components.append(subcomponent)
            return tuple(self.subcomponents.values()), inline_components
        return (), ()

    def check(self, source_component:"Component", trace:Trace) -> None:
        with trace.enter_keys(self.trace_path, self.subcomponents_data):
            super().check(source_component, trace)
            if self.has_reference_components and self.allow_inline is InlinePermissions.inline:
                trace.exception(Exceptions.ReferenceComponentError(source_component, self))
            if self.has_inline_components and self.allow_inline is InlinePermissions.reference:
                trace.exception(Exceptions.InlineComponentError(source_component, self))

    def for_each[b](self, function:Callable[[str, a],b]) -> None:
        '''
        Calls the given function on each Component in this Field.
        :function: The function to use.
        '''
        for key, subcomponent in self.subcomponents.items():
            function(key, subcomponent)

    def map[b](self, function:Callable[[str, a],b]) -> Iterator[tuple[str,b]]:
        '''
        Calls the given function on each Component in this Field, and returns the results in the same order.
        :function: The function to use.
        '''
        return zip(self.subcomponents.keys(), starmap(function, self.subcomponents.items()))

    def check_coverage[b](self, get_final_function:Callable[[a],b], linked_requirements:dict[str,type[b]], trace:Trace) -> None:
        '''
        :get_final_function: A function that turns the Components referenced in this Field into their finals.
        :linked_requirements: The dictionary that verifies the validity of this Field's Components.
        '''
        with trace.enter_keys(self.trace_path, self.subcomponents_data):
            linked_objects:dict[str,b] = {key: get_final_function(linked_component) for key, linked_component in self.subcomponents.items()}
            for key, linked_type in linked_requirements.items():
                with trace.enter_key(key, linked_type):
                    if key not in linked_objects:
                        trace.exception(Exceptions.LinkedComponentMissingError(key, linked_type))
            for key, linked_object in linked_objects.items():
                with trace.enter_key(key, linked_object):
                    if key not in linked_requirements:
                        Exceptions.LinkedComponentExtraError(key, linked_object, [key for key in linked_objects if key not in linked_requirements])
                    required_type = linked_requirements.get(key)
                    if required_type is not None and not isinstance(linked_object, required_type):
                        Exceptions.LinkedComponentTypeError(key, required_type, linked_object)

    def check_coverage_types[b](self, get_final_function:Callable[[a],type[b]], linked_requirements:dict[str,type[b]], trace:Trace) -> None:
        '''
        :get_final_function: A function that turns the Components referenced in this Field into their finals.
        :linked_requirements: The dictionary that verifies the validity of this Field's Components.
        '''
        with trace.enter_keys(self.trace_path, self.subcomponents_data):
            linked_objects:dict[str,type[b]] = {key: get_final_function(linked_component) for key, linked_component in self.subcomponents.items()}
            for key, linked_type in linked_requirements.items():
                with trace.enter_key(key, linked_type):
                    if key not in linked_objects:
                        trace.exception(Exceptions.LinkedComponentMissingError(key, linked_type))
            for key, linked_object in linked_objects.items():
                with trace.enter_key(key, linked_object):
                    if key not in linked_requirements:
                        trace.exception(Exceptions.LinkedComponentExtraError(key, linked_object, [key for key in linked_objects if key not in linked_requirements]))
                    required_type = linked_requirements.get(key)
                    if required_type is not None and not issubclass(linked_object, required_type):
                        trace.exception(Exceptions.LinkedComponentTypeError(key, required_type, linked_object))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} len {len(self)} id {id(self)}>"

    def __len__(self) -> int:
        return 0 if self.subcomponents is None else len(self.subcomponents)
