from typing import Callable, Iterator, Sequence, cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.ScriptImporter as ScriptImporter
import Utilities.Exceptions as Exceptions


class ComponentListField[a:Component.Component](Field.Field):
    '''A link to multiple other Components.'''

    __slots__ = (
        "allow_inline",
        "assume_component_group",
        "assume_type",
        "has_inline_components",
        "has_reference_components",
        "pattern",
        "subcomponents",
        "subcomponents_data",
    )

    def __init__(
        self,
        subcomponents_data:Sequence[str|ComponentTyping.ComponentTypedDicts]|str|ComponentTyping.ComponentTypedDicts,
        pattern:Pattern.Pattern[a],
        path:list[str|int],
        *,
        allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed,
        assume_type:str|None=None,
        assume_component_group:str|None=None,
    ) -> None:
        '''
        :subcomponents_data: The names of the reference Components and/or data of the inline Components this Field refers to.
        :pattern: The Pattern used to search for Components.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        :assume_type: String to use as the type of an inline Component if the type key is missing from it.
        :assume_component_group: Assumed Component group if it is not specified.
        '''
        super().__init__(path)
        self.subcomponents_data = cast(Sequence[str|ComponentTyping.ComponentTypedDicts], [subcomponents_data]) if isinstance(subcomponents_data, (str, dict)) else subcomponents_data
        self.subcomponents:list[a]
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
        self.subcomponents = []
        inline_components:list[a] = []
        for subcomponent_data in self.subcomponents_data:
            subcomponent, is_inline = Field.choose_component(subcomponent_data, source_component, self.pattern, components, global_components, self.error_path, create_component_function, self.assume_type, self.assume_component_group)
            self.has_reference_components = self.has_reference_components or not is_inline
            self.has_inline_components = self.has_inline_components or is_inline
            self.subcomponents.append(subcomponent)
            if is_inline:
                inline_components.append(subcomponent)
        return self.subcomponents, inline_components

    def check(self, source_component:"Component.Component") -> list[Exception]:
        exceptions:list[Exception] = super().check(source_component)
        if self.has_reference_components and self.allow_inline is Field.InlinePermissions.inline:
            exceptions.append(Exceptions.ReferenceComponentError(source_component, self))
        if self.has_inline_components and self.allow_inline is Field.InlinePermissions.reference:
            exceptions.append(Exceptions.InlineComponentError(source_component, self))
        return exceptions

    def extend(self, new_components:Sequence[a]) -> None:
        '''
        Adds new components to this Field.
        :new_components: The sequence of Components to add.
        '''
        self.subcomponents.extend(new_components)

    def for_each[b](self, function:Callable[[a],b]) -> None:
        '''
        Calls the given function on each Component in this Field.
        :function: The function to use.
        '''
        for subcomponent in self.subcomponents:
            function(subcomponent)

    def map[b](self, function:Callable[[a],b]) -> Iterator[b]:
        '''
        Calls the given function on each Component in this Field, and returns the results in the same order.
        :function: The function to use.
        '''
        return map(function, self.subcomponents)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} len {len(self)} id {id(self)}>"

    def __len__(self) -> int:
        if self.subcomponents is None: return 0
        return len(self.subcomponents)
