from typing import Callable, Generic, MutableSequence, Sequence, TypeVar

import Structure.Importer.Component as Component
import Structure.Importer.Field.Field as Field
import Structure.Importer.ImporterConfig as ImporterConfig

a = TypeVar("a", bound=Field.Field, covariant=True)

class FieldContainer(Field.Field, Generic[a]):
    '''
    Abstract class of Field that contains other Fields.
    '''

    def __init__(self, fields:MutableSequence[a], path: list[str | int]) -> None:
        super().__init__(path)
        self.fields = fields

    def set_field(self, component_name:str, component_class_name:str, components:dict[str,"Component.Component"], functions:dict[str,Callable]) -> Sequence["Component.Component"]:
        linked_components:list["Component.Component"] = []
        for field in self.fields:
            linked_components.extend(field.set_field(component_name, component_class_name, components, functions))
        return linked_components

    def resolve(self) -> None:
        for field in self.fields:
            field.resolve()

    def check(self, component_name:str, component_class_name:str, config:ImporterConfig.ImporterConfig) -> list[Exception]:
        exceptions:list[Exception] = []
        for field in self.fields:
            exceptions.extend(field.check(component_name, component_class_name, config))
        return exceptions

    def __repr__(self) -> str:
        return "<%s len %i id %i>" % (self.__class__.__name__, len(self.fields), id(self))
