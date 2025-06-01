from typing import Callable, Self, Sequence, cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.FieldContainer as FieldContainer
import Component.Pattern as Pattern
import Component.ScriptImporter as ScriptImporter
import Component.Structure.Field.AbstractTypeField as AbstractTypeField
import Component.Structure.StructureComponent as StructureComponent
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace


class ComponentField[a: Component.Component](Field.Field):
    '''A link to another Component.'''

    __slots__ = (
        "allow_inline",
        "assume_component_group",
        "assume_type",
        "has_inline_components",
        "has_reference_components",
        "pattern",
        "subcomponent",
        "subcomponent_data",
    )

    def __init__(
        self,
        subcomponent_data:str|ComponentTyping.ComponentTypedDicts,
        pattern:Pattern.Pattern[a],
        path:tuple[str,...],
        *,
        allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed,
        assume_type:str|None=None,
        assume_component_group:str|None=None,
    ) -> None:
        '''
        :subcomponent_data: The name of the reference Component or data of the inline Component.
        :pattern: The Pattern used to search for Components.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        :assume_type: String to use as the type of an inline Component if the type key is missing from it.
        :assume_component_group: Assumed Component group if it is not specified.
        '''
        super().__init__(path)
        self.subcomponent_data = subcomponent_data
        self.subcomponent:a # can only be accessed after the set_field stage
        self.pattern = pattern
        self.allow_inline = allow_inline
        self.has_reference_components = False
        self.has_inline_components = False
        self.assume_type = assume_type
        self.assume_component_group = assume_component_group

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
        trace:Trace.Trace,
    ) -> tuple[Sequence[a],Sequence[a]]:
        with trace.enter_keys(self.trace_path, self.subcomponent_data):
            subcomponent, is_inline = Field.choose_component(self.subcomponent_data, source_component, self.pattern, components, global_components, trace, self.trace_path, create_component_function, self.assume_type, self.assume_component_group)
            if subcomponent is ...:
                return (), ()
            self.subcomponent = subcomponent
            self.has_reference_components = self.has_reference_components or not is_inline
            self.has_inline_components = self.has_inline_components or is_inline
            return (self.subcomponent,), ((self.subcomponent,) if is_inline else ())
        return (), ()

    def check(self, source_component:"Component.Component", trace:Trace.Trace) -> None:
        with trace.enter_keys(self.trace_path, ...):
            super().check(source_component, trace)
            if self.has_reference_components and self.allow_inline is Field.InlinePermissions.inline:
                trace.exception(Exceptions.ReferenceComponentError(source_component, self, cast(str, self.subcomponent_data)))
            if self.has_inline_components and self.allow_inline is Field.InlinePermissions.reference:
                trace.exception(Exceptions.InlineComponentError(source_component, self, cast(ComponentTyping.ComponentTypedDicts, self.subcomponent_data)))

class OptionalComponentField[a: Component.Component](FieldContainer.FieldContainer):

    __slots__ = (
        "component_field",
    )

    def __init__(
            self,
            subcomponent_data:str|ComponentTyping.ComponentTypedDicts|None,
            pattern:Pattern.Pattern[a],
            path:tuple[str,...],
            *,
            allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed,
            assume_type:str|None=None,
            assume_component_group:str|None=None,
        ) -> None:
        '''
        :subcomponent_data: The name of the reference Component, data of the inline Component, or None.
        :pattern: The Pattern used to search for Components.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        :assume_type: String to use as the type of an inline Component if the type key is missing from it.
        :assume_component_group: Assumed Component group if it is not specified.
        '''
        self.component_field:ComponentField|None
        if subcomponent_data is None:
            self.component_field = None
            super().__init__([], path)
        else:
            self.component_field = ComponentField(subcomponent_data, pattern, path, allow_inline=allow_inline, assume_type=assume_type, assume_component_group=assume_component_group)
            super().__init__([self.component_field], path)

    def map[b](self, function:Callable[[a],b]=lambda component: component.final) -> b|None:
        return None if self.component_field is None else function(self.component_field.subcomponent)

    @property
    def subcomponent_data(self) -> str|ComponentTyping.ComponentTypedDicts|None:
        return None if self.component_field is None else self.component_field.subcomponent_data

    @property
    def subcomponent(self) -> a|None:
        return None if self.component_field is None else self.component_field.subcomponent

    @property
    def exists(self) -> bool:
        return self.component_field is not None
