from typing import Callable, Generic, MutableSequence, TypeVar

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field

a = TypeVar("a", bound=Field.Field, covariant=True)

class FieldContainer(Field.Field, Generic[a]):
    '''
    Abstract class of Field that contains other Fields.
    '''

    def __init__(self, fields:MutableSequence[a], path: list[str | int]) -> None:
        super().__init__(path)
        self.fields = fields

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["Component.Component"],list["Component.Component"]]:
        linked_components:list["Component.Component"] = []
        inline_components:list["Component.Component"] = []
        for field in self.fields:
            new_linked_components, new_inline_components = field.set_field(source_component, components, imported_components, functions, create_component_function)
            linked_components.extend(new_linked_components)
            inline_components.extend(new_inline_components)
        return linked_components, inline_components

    def resolve_create_finals(self) -> None:
        for field in self.fields:
            field.resolve_link_finals()

    def resolve_link_finals(self) -> None:
        for field in self.fields:
            field.resolve_link_finals()

    def check(self, source_component:"Component.Component") -> list[Exception]:
        exceptions:list[Exception] = super().check(source_component)
        for field in self.fields:
            exceptions.extend(field.check(source_component))
        return exceptions

    def __repr__(self) -> str:
        return "<%s len %i id %i>" % (self.__class__.__name__, len(self.fields), id(self))
