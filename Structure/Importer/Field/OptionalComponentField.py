from typing import Callable, Generic, TypeVar, cast

import Structure.Importer.Component as Component
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.Field as Field
import Structure.Importer.Pattern as Pattern
import Utilities.Exceptions as Exceptions

a = TypeVar("a", bound=Component.Component, covariant=True)

class OptionalComponentField(Field.Field, Generic[a]):
    '''A link to another Component.'''

    def __init__(self, subcomponent_data:str|ComponentTyping.ComponentTypedDicts|None, pattern:Pattern.Pattern[a], path:list[str|int], *, allow_in_line:Field.InLinePermissions=Field.InLinePermissions.mixed) -> None:
        '''
        :subcomponent_data: The name of the reference Component or the data of the in-line Components this Field refers to.
        :pattern: The Pattern used to search for Components.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        :allow_in_line: An InLinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__(path)
        self.subcomponent_data = subcomponent_data
        self.subcomponent:a|None = None
        self.pattern = pattern
        self.has_set_component = False
        self.allow_in_line = allow_in_line
        self.has_reference_components = False
        self.has_in_line_components = False

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list[a],list[a]]:
        self.has_set_component = True
        if self.subcomponent_data is None:
            self.subcomponent = None
            return [], []
        else:
            self.subcomponent, is_in_line = Field.choose_component(self.subcomponent_data, source_component, self.pattern, components, imported_components, self.error_path, create_component_function)
            self.has_reference_components = self.has_reference_components or not is_in_line
            self.has_in_line_components = self.has_in_line_components or is_in_line
            return [self.subcomponent], ([self.subcomponent] if is_in_line else [])

    def check(self, source_component:"Component.Component") -> list[Exception]:
        exceptions:list[Exception] = super().check(source_component)
        if self.has_reference_components and self.allow_in_line is Field.InLinePermissions.in_line:
            exceptions.append(Exceptions.ReferenceComponentError(source_component, self, cast(str, self.subcomponent_data)))
        if self.has_in_line_components and self.allow_in_line is Field.InLinePermissions.reference:
            exceptions.append(Exceptions.InLineComponentError(source_component, self, cast(ComponentTyping.ComponentTypedDicts, self.subcomponent_data)))
        return exceptions

    def get_component(self) -> a|None:
        '''
        Returns the Component that this Field refers to.
        Can only be called after `set_field`.
        '''
        if not self.has_set_component:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.get_component, self)
        return self.subcomponent
