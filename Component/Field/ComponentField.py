from typing import cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.ScriptImporter as ScriptImporter
import Utilities.Exceptions as Exceptions


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
        path:list[str|int],
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
    ) -> tuple[list[a],list[a]]:
        self.subcomponent, is_inline = Field.choose_component(self.subcomponent_data, source_component, self.pattern, components, global_components, self.error_path, create_component_function, self.assume_type, self.assume_component_group)
        self.has_reference_components = self.has_reference_components or not is_inline
        self.has_inline_components = self.has_inline_components or is_inline
        return [self.subcomponent], ([self.subcomponent] if is_inline else [])

    def check(self, source_component:"Component.Component") -> list[Exception]:
        exceptions:list[Exception] = super().check(source_component)
        if self.has_reference_components and self.allow_inline is Field.InlinePermissions.inline:
            exceptions.append(Exceptions.ReferenceComponentError(source_component, self, cast(str, self.subcomponent_data)))
        if self.has_inline_components and self.allow_inline is Field.InlinePermissions.reference:
            exceptions.append(Exceptions.InlineComponentError(source_component, self, cast(ComponentTyping.ComponentTypedDicts, self.subcomponent_data)))
        return exceptions
