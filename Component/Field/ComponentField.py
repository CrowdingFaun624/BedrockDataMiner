from typing import Callable, Generic, TypeVar, Union, cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Utilities.Exceptions as Exceptions

a = TypeVar("a", bound=Component.Component, covariant=True)

class ComponentField(Field.Field, Generic[a]):
    '''A link to another Component.'''

    def __init__(self, subcomponent_data:str|ComponentTyping.ComponentTypedDicts, pattern:Pattern.Pattern[a], path:list[str|int], *, allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed, assume_type:str|None=None) -> None:
        '''
        :subcomponent_data: The name of the reference Component or data of the inline Component.
        :pattern: The Pattern used to search for Components.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        :assume_type: String to use as the type of an inline Component if the type key is missing from it.
        '''
        super().__init__(path)
        self.subcomponent_data = subcomponent_data
        self.subcomponent:Union[a,None] = None
        self.pattern = pattern
        self.allow_inline = allow_inline
        self.has_reference_components = False
        self.has_inline_components = False
        self.assume_type = assume_type

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list[a],list[a]]:
        self.subcomponent, is_inline = Field.choose_component(self.subcomponent_data, source_component, self.pattern, components, imported_components, self.error_path, create_component_function, self.assume_type)
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

    def get_component(self) -> a:
        '''
        Returns the Component that this Field refers to.
        Can only be called after `set_field`.
        '''
        if self.subcomponent is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.get_component, self)
        return self.subcomponent
