from typing import TYPE_CHECKING, Mapping, Sequence

from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction
from Component.Field.Field import choose_component
from Component.Permissions import InlineUsage
from Component.ScriptImporter import ScriptSetSet
from Component.Structure.Field.AbstractTypeField import (
    TYPE_ALIAS_PATTERN,
    AbstractTypeField,
)
from Component.Structure.TypeAliasComponent import TypeAliasComponent
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

class TypeField(AbstractTypeField):
    '''A link to a TypeAliasComponent or type.'''

    __slots__ = ()

    def __init__(self, subcomponent_data:str, path:tuple[str,...], cumulative_path:tuple[str,...]|None=None) -> None:
        '''
        :subcomponent_data: String representing a default type or Component.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        '''
        super().__init__(subcomponent_data, path, cumulative_path)

    def set_field(
        self,
        source_component:"Component",
        local_group:"Group",
        global_groups:Mapping[str,Mapping[str,"Group"]],
        functions:"ScriptSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["TypeAliasComponent"],Sequence["TypeAliasComponent"]]:
        with trace.enter_keys(self.trace_path, self.subcomponent_data):
            if self.subcomponent_data in self.domain.type_stuff.default_types:
                self._types = (self.domain.type_stuff.default_types[self.subcomponent_data],)
                return (), ()
            else:
                component, inline_usage, inheritance_usage = choose_component(self.subcomponent_data, source_component, TYPE_ALIAS_PATTERN, local_group, global_groups, trace, self.cumulative_path,
                    functions, create_component_function, None, self.domain.type_stuff.default_types)
                if component is ...:
                    return (), ()
                component.check_permissions(self, inline_usage, inheritance_usage, trace)
                self._types = (component,)
                return (component,), (component,) if inline_usage is InlineUsage.inline else ()
        return (), ()
