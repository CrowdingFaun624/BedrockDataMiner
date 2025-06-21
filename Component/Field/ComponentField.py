from typing import TYPE_CHECKING, Callable, Sequence, cast

import Utilities.Exceptions as Exceptions
from Component.Component import Component
from Component.ComponentTyping import ComponentTypedDicts, CreateComponentFunction
from Component.Field.Field import Field, InlinePermissions, choose_component
from Component.Field.FieldContainer import FieldContainer
from Component.Pattern import Pattern
from Component.ScriptImporter import ScriptSetSetSet
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

class ComponentField[a: Component](Field):
    '''A link to another Component.'''

    __slots__ = (
        "allow_inline",
        "assume_type",
        "has_inline_components",
        "has_reference_components",
        "pattern",
        "subcomponent",
        "subcomponent_data",
    )

    def __init__(
        self,
        subcomponent_data:str|ComponentTypedDicts,
        pattern:Pattern[a],
        path:tuple[str,...],
        cumulative_path:tuple[str,...]|None=None,
        *,
        allow_inline:InlinePermissions=InlinePermissions.mixed,
        assume_type:str|None=None,
    ) -> None:
        '''
        :subcomponent_data: The name of the reference Component or data of the inline Component.
        :pattern: The Pattern used to search for Components.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        :assume_type: String to use as the type of an inline Component if the type key is missing from it.
        '''
        super().__init__(path, cumulative_path)
        self.subcomponent_data = subcomponent_data
        self.subcomponent:a # can only be accessed after the set_field stage
        self.pattern = pattern
        self.allow_inline = allow_inline
        self.has_reference_components = False
        self.has_inline_components = False
        self.assume_type = assume_type

    def set_field(
        self,
        source_component:"Component",
        local_group:"Group",
        global_groups:dict[str,dict[str,"Group"]],
        functions:"ScriptSetSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence[a],Sequence[a]]:
        with trace.enter_keys(self.trace_path, self.subcomponent_data):
            subcomponent, is_inline = choose_component(self.subcomponent_data, source_component, self.pattern, local_group, global_groups, trace, self.trace_path, create_component_function, self.assume_type)
            if subcomponent is ...:
                return (), ()
            self.subcomponent = subcomponent
            self.has_reference_components = self.has_reference_components or not is_inline
            self.has_inline_components = self.has_inline_components or is_inline
            return (self.subcomponent,), ((self.subcomponent,) if is_inline else ())
        return (), ()

    def check(self, source_component:"Component", trace:Trace) -> None:
        with trace.enter_keys(self.trace_path, ...):
            super().check(source_component, trace)
            if self.has_reference_components and self.allow_inline is InlinePermissions.inline:
                trace.exception(Exceptions.ReferenceComponentError(source_component, self, cast(str, self.subcomponent_data)))
            if self.has_inline_components and self.allow_inline is InlinePermissions.reference:
                trace.exception(Exceptions.InlineComponentError(source_component, self, cast(ComponentTypedDicts, self.subcomponent_data)))

class OptionalComponentField[a: Component](FieldContainer):

    __slots__ = (
        "component_field",
    )

    def __init__(
            self,
            subcomponent_data:str|ComponentTypedDicts|None,
            pattern:Pattern[a],
            path:tuple[str,...],
            cumulative_path:tuple[str,...]|None=None,
            *,
            allow_inline:InlinePermissions=InlinePermissions.mixed,
            assume_type:str|None=None,
        ) -> None:
        '''
        :subcomponent_data: The name of the reference Component, data of the inline Component, or None.
        :pattern: The Pattern used to search for Components.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        :assume_type: String to use as the type of an inline Component if the type key is missing from it.
        '''
        self.component_field:ComponentField|None
        if subcomponent_data is None:
            self.component_field = None
            super().__init__([], path, cumulative_path)
        else:
            self.component_field = ComponentField(subcomponent_data, pattern, path, cumulative_path, allow_inline=allow_inline, assume_type=assume_type)
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
