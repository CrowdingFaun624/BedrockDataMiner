from typing import Sequence, cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Component.Structure.Field.AbstractTypeField as AbstractTypeField
import Component.Structure.TypeAliasComponent as TypeAliasComponent
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace


class TypeListField(AbstractTypeField.AbstractTypeField):
    '''A link to multiple TypeAliasComponents and/or types.'''

    __slots__ = (
        "_types",
        "primitive_types",
        "type_aliases",
    )

    def __init__(self, subcomponents_strs:Sequence[str]|str, path:tuple[str,...]) -> None:
        '''
        :subcomponents_strs: List of string representing a default type or Component.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__((subcomponents_strs,) if isinstance(subcomponents_strs, str) else subcomponents_strs, path)
        self.primitive_types:list[type]
        self.type_aliases:list[TypeAliasComponent.TypeAliasComponent]

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
        trace:Trace.Trace,
    ) -> tuple[Sequence["TypeAliasComponent.TypeAliasComponent"],Sequence["TypeAliasComponent.TypeAliasComponent"]]:
        with trace.enter_keys(self.trace_path, self.subcomponent_data):
            components_used:list["TypeAliasComponent.TypeAliasComponent"] = []
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
                        subcomponent, is_inline = Field.choose_component(subcomponent_data, source_component, TypeAliasComponent.TYPE_ALIAS_PATTERN, components, global_components, trace, self.trace_path, create_component_function, None, None, self.domain.type_stuff.default_types)
                        if subcomponent is ...:
                            continue
                        if is_inline:
                            trace.exception(Exceptions.InlineComponentError(source_component, self, cast(ComponentTyping.TypeAliasTypedDict, subcomponent_data)))
                        components_used.append(subcomponent)
                        self.type_aliases.append(subcomponent)
            return components_used, ()
        return (), ()

    def resolve_link_finals(self, trace:Trace.Trace) -> None:
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
