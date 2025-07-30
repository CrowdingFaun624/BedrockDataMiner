from typing import TYPE_CHECKING, Callable, Mapping, Sequence

from Component.Component import Component
from Component.ComponentTyping import ComponentTypedDicts, CreateComponentFunction
from Component.Field.Field import Field, choose_component
from Component.Field.FieldContainer import FieldContainer
from Component.Pattern import AbstractPattern
from Component.Permissions import InlineUsage
from Component.ScriptImporter import ScriptSetSet
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

class ComponentField[a: Component](Field):
    '''A link to another Component.'''

    __slots__ = (
        "assume_type",
        "pattern",
        "subcomponent",
        "subcomponent_data",
    )

    def __init__(
        self,
        subcomponent_data:str|ComponentTypedDicts,
        pattern:AbstractPattern[a],
        path:tuple[str,...],
        cumulative_path:tuple[str,...]|None=None,
        *,
        assume_type:str|None=None,
    ) -> None:
        '''
        :subcomponent_data: The name of the reference Component or data of the inline Component.
        :pattern: The Pattern used to search for Components.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        :assume_type: String to use as the type of an inline Component if the type key is missing from it.
        '''
        super().__init__(path, cumulative_path)
        self.subcomponent_data = subcomponent_data
        self.subcomponent:a # can only be accessed after the set_field stage
        self.pattern = pattern
        self.assume_type = assume_type

    def set_field(
        self,
        source_component:"Component",
        local_group:"Group",
        global_groups:Mapping[str,Mapping[str,"Group"]],
        functions:"ScriptSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence[a],Sequence[a]]:
        with trace.enter_keys(self.trace_path, self.subcomponent_data):
            subcomponent, inline_usage, inheritance_usage = choose_component(self.subcomponent_data, source_component, self.pattern, local_group, global_groups, trace, self.cumulative_path, functions, create_component_function, self.assume_type)
            if subcomponent is ...:
                return (), ()
            subcomponent.check_permissions(self, inline_usage, inheritance_usage, trace)
            self.subcomponent = subcomponent
            return (self.subcomponent,), ((self.subcomponent,) if inline_usage is InlineUsage.inline else ())
        return (), ()

class OptionalComponentField[a: Component](FieldContainer):

    __slots__ = (
        "component_field",
    )

    def __init__(
            self,
            subcomponent_data:str|ComponentTypedDicts|None,
            pattern:AbstractPattern[a],
            path:tuple[str,...],
            cumulative_path:tuple[str,...]|None=None,
            *,
            assume_type:str|None=None,
        ) -> None:
        '''
        :subcomponent_data: The name of the reference Component, data of the inline Component, or None.
        :pattern: The Pattern used to search for Components.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        :assume_type: String to use as the type of an inline Component if the type key is missing from it.
        '''
        self.component_field:ComponentField|None
        if subcomponent_data is None:
            self.component_field = None
            super().__init__([], path, cumulative_path)
        else:
            self.component_field = ComponentField(subcomponent_data, pattern, path, cumulative_path, assume_type=assume_type)
            super().__init__([self.component_field], path, cumulative_path)

    def map[b](self, function:Callable[[a],b]=lambda component: component.final) -> b|None:
        return None if self.component_field is None else function(self.component_field.subcomponent)

    @property
    def subcomponent_data(self) -> str|ComponentTypedDicts|None:
        return None if self.component_field is None else self.component_field.subcomponent_data

    @property
    def subcomponent(self) -> a|None:
        return None if self.component_field is None else self.component_field.subcomponent

    @property
    def exists(self) -> bool:
        return self.component_field is not None
