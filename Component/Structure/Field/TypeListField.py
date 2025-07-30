from typing import TYPE_CHECKING, Mapping, Sequence

import Utilities.Exceptions as Exceptions
from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction
from Component.Field.Field import choose_component
from Component.Permissions import InlineUsage
from Component.ScriptImporter import ScriptSetSet
from Component.Structure.Field.AbstractTypeField import (
    TYPE_ALIAS_PATTERN,
    AbstractTypeField,
)
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group
    from Component.Structure.TypeAliasComponent import TypeAliasComponent

class TypeListField(AbstractTypeField):
    '''A link to multiple TypeAliasComponents and/or types.'''

    __slots__ = ()

    def __init__(self, subcomponents_strs:Sequence[str]|str, path:tuple[str,...], cumulative_path:tuple[str,...]|None=None) -> None:
        '''
        :subcomponents_strs: List of string representing a default type or Component.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        '''
        super().__init__((subcomponents_strs,) if isinstance(subcomponents_strs, str) else subcomponents_strs, path, cumulative_path)

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
            components_used:list["TypeAliasComponent"] = []
            already_types:set[str] = set()
            subcomponents:list["type|TypeAliasComponent"] = []
            inline_components:list["TypeAliasComponent"] = []
            for index, subcomponent_data in enumerate(self.subcomponent_data):
                with trace.enter_keys(self.trace_path, subcomponent_data):
                    if subcomponent_data in already_types:
                        trace.exception(Exceptions.ComponentDuplicateTypeError(subcomponent_data))
                    already_types.add(subcomponent_data)
                    if subcomponent_data in self.domain.type_stuff.default_types:
                        subcomponent_type = self.domain.type_stuff.default_types[subcomponent_data]
                        subcomponents.append(subcomponent_type)
                    else:
                        subcomponent, inline_usage, inheritance_usage = choose_component(subcomponent_data, source_component, TYPE_ALIAS_PATTERN, local_group, global_groups, trace,
                            (*self.cumulative_path, str(index)), functions, create_component_function, None, self.domain.type_stuff.default_types)
                        if subcomponent is ...:
                            continue
                        subcomponent.check_permissions(self, inline_usage, inheritance_usage, trace)
                        if inline_usage is InlineUsage.inline:
                            inline_components.append(subcomponent)
                        components_used.append(subcomponent)
                        subcomponents.append(subcomponent)
            self._types = subcomponents
            return components_used, inline_components
        return (), ()

    def __len__(self) -> int:
        return len(self.types)
