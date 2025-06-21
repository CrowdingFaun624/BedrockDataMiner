from typing import TYPE_CHECKING, Sequence, cast

from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction, TypeAliasTypedDict
from Component.Field.Field import choose_component
from Component.ScriptImporter import ScriptSetSetSet
from Component.Structure.Field.AbstractTypeField import AbstractTypeField
from Component.Structure.TypeAliasComponent import (
    TYPE_ALIAS_PATTERN,
    TypeAliasComponent,
)
from Utilities.Exceptions import InlineComponentError
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

class TypeField(AbstractTypeField):
    '''A link to a TypeAliasComponent or type.'''

    __slots__ = (
        "_types",
        "subcomponent",
        "subcomponent_data",
    )

    def __init__(self, subcomponent_data:str, path:tuple[str,...]) -> None:
        '''
        :subcomponent_data: String representing a default type or Component.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(subcomponent_data, path)
        self.subcomponent:type|TypeAliasComponent

    def set_field(
        self,
        source_component:"Component",
        local_group:"Group",
        global_groups:dict[str,dict[str,"Group"]],
        functions:"ScriptSetSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["TypeAliasComponent"],Sequence["TypeAliasComponent"]]:
        with trace.enter_keys(self.trace_path, self.subcomponent_data):
            if self.subcomponent_data in self.domain.type_stuff.default_types:
                self.subcomponent = self.domain.type_stuff.default_types[self.subcomponent_data]
                return (), ()
            else:
                component, is_inline = choose_component(self.subcomponent_data, source_component, TYPE_ALIAS_PATTERN, local_group, global_groups, trace, self.trace_path,
                                                              create_component_function, None, self.domain.type_stuff.default_types)
                if component is ...:
                    return (), ()
                if is_inline:
                    trace.exception(InlineComponentError(source_component, self, cast(TypeAliasTypedDict, self.subcomponent_data)))
                    return (), ()
                self.subcomponent = component
                return (component,), ()
        return (), ()

    def resolve_link_finals(self, trace:Trace) -> None:
        with trace.enter_keys(self.trace_path, self.subcomponent_data):
            self._types = (self.subcomponent,) if isinstance(self.subcomponent, type) else self.subcomponent.final
            if self.type_set is not None:
                self.type_set.update(self._types)
