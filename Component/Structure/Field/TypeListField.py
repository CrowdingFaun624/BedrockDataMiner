from typing import TYPE_CHECKING, Sequence, cast

import Utilities.Exceptions as Exceptions
from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction, TypeAliasTypedDict
from Component.Field.Field import choose_component
from Component.ScriptImporter import ScriptSetSetSet
from Component.Structure.Field.AbstractTypeField import AbstractTypeField
from Component.Structure.TypeAliasComponent import (
    TYPE_ALIAS_PATTERN,
    TypeAliasComponent,
)
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

class TypeListField(AbstractTypeField):
    '''A link to multiple TypeAliasComponents and/or types.'''

    __slots__ = (
        "_types",
        "primitive_types",
        "type_aliases",
    )

    def __init__(self, subcomponents_strs:Sequence[str]|str, path:tuple[str,...], cumulative_path:tuple[str,...]|None=None) -> None:
        '''
        :subcomponents_strs: List of string representing a default type or Component.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        '''
        super().__init__((subcomponents_strs,) if isinstance(subcomponents_strs, str) else subcomponents_strs, path)
        self.primitive_types:list[type]
        self.type_aliases:list[TypeAliasComponent]

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
            components_used:list["TypeAliasComponent"] = []
            self.primitive_types = []
            self.type_aliases = []
            already_types:set[str] = set()
            for subcomponent_data in self.subcomponent_data:
                with trace.enter_keys(self.trace_path, subcomponent_data):
                    if subcomponent_data in already_types:
                        trace.exception(Exceptions.ComponentDuplicateTypeError(subcomponent_data))
                    already_types.add(subcomponent_data)
                    if subcomponent_data in self.domain.type_stuff.default_types:
                        subcomponent_type = self.domain.type_stuff.default_types[subcomponent_data]
                        self.primitive_types.append(subcomponent_type)
                    else:
                        subcomponent, is_inline = choose_component(subcomponent_data, source_component, TYPE_ALIAS_PATTERN, local_group, global_groups, trace, self.trace_path, create_component_function, None, self.domain.type_stuff.default_types)
                        if subcomponent is ...:
                            continue
                        if is_inline:
                            trace.exception(Exceptions.InlineComponentError(source_component, self, cast(TypeAliasTypedDict, subcomponent_data)))
                            continue
                        components_used.append(subcomponent)
                        self.type_aliases.append(subcomponent)
            return components_used, ()
        return (), ()

    def resolve_link_finals(self, trace:Trace) -> None:
        with trace.enter_keys(self.trace_path, self.subcomponent_data):
            types:list[type] = []
            types.extend(self.primitive_types)
            for type_alias_component in self.type_aliases:
                types.extend(type_alias_component.final)
            self._types = tuple(types)
            if self.type_set is not None:
                self.type_set.update(self._types)

    def __len__(self) -> int:
        return len(self.types)
