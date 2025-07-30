from typing import TYPE_CHECKING, Mapping, MutableSequence, Sequence

from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction
from Component.Field.Field import Field
from Component.ScriptImporter import ScriptSetSet
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

class FieldContainer[a: Field](Field):
    '''
    Abstract class of Field that contains other Fields.
    '''

    __slots__ = (
        "fields",
    )

    def __init__(self, fields:MutableSequence[a], path: tuple[str,...], cumulative_path:tuple[str,...]|None=None) -> None:
        '''
        :fields: The sequence of Fields to store in this Field.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        '''
        super().__init__(path, cumulative_path)
        self.fields = fields

    def set_component(self, component:"Component") -> None:
        super().set_component(component)
        for field in self.fields:
            field.set_component(component)

    def set_field(
        self,
        source_component:"Component",
        local_group:"Group",
        global_groups:Mapping[str,Mapping[str,"Group"]],
        functions:"ScriptSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["Component"],Sequence["Component"]]:
        with trace.enter_keys(self.trace_path, ...):
            linked_components:list["Component"] = []
            inline_components:list["Component"] = []
            for field in self.fields:
                new_linked_components, new_inline_components = field.set_field(source_component, local_group, global_groups, functions, create_component_function, trace)
                linked_components.extend(new_linked_components)
                inline_components.extend(new_inline_components)
            return linked_components, inline_components
        return (), ()

    def resolve_link_finals(self, trace:Trace) -> None:
        with trace.enter_keys(self.trace_path, ...):
            for field in self.fields:
                field.resolve_link_finals(trace)

    def check(self, source_component:"Component", trace:Trace) -> None:
        with trace.enter_keys(self.trace_path, ...):
            super().check(source_component, trace)
            for field in self.fields:
                field.check(source_component, trace)

    def finalize(self, trace: Trace) -> None:
        with trace.enter_keys(self.trace_path, ...):
            super().finalize(trace)
            for field in self.fields:
                field.finalize(trace)
