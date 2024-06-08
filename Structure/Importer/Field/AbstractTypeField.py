from typing import TYPE_CHECKING, TypeAlias

import Structure.Importer.Field.Field as Field
import Structure.Importer.Field.OptionalStructroidComponentField as OptionalStructroidComponentField
import Structure.Importer.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Structure.Importer.Field.StructroidComponentField as StructroidComponentField
import Structure.Importer.Field.StructureComponentField as StructureComponentField
import Structure.Importer.StructureComponent as StructureComponent
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Importer.Component as Component

VerifyComponentType:TypeAlias = StructroidComponentField.StructroidComponentField|OptionalStructroidComponentField.OptionalStructroidComponentField|StructureComponentField.StructureComponentField|OptionalStructureComponentField.OptionalStructureComponentField

class AbstractTypeField(Field.Field):

    def __init__(self, path: list[str | int]) -> None:
        super().__init__(path)
        self.verify_with_component:VerifyComponentType|None=None

    def check(self, source_component:"Component.Component") -> list[Exception]:
        exceptions = super().check(source_component)
        if self.verify_with_component is not None:
            subcomponent = self.verify_with_component.get_component()
            component_types = self.get_types()
            if subcomponent is None:
                for value_type in component_types:
                    if value_type in StructureComponent.REQUIRES_SUBCOMPONENT_TYPES:
                        exceptions.append(Exceptions.ComponentTypeRequiresComponentError(source_component, value_type))
            else:
                if set(component_types) != set(subcomponent.my_type):
                    exceptions.append(Exceptions.ComponentMismatchedTypesError(source_component, sorted(component_types, key=lambda type: type.__name__), subcomponent, sorted(subcomponent.my_type, key=lambda type: type.__name__)))
        return exceptions

    def resolve(self) -> None:
        '''
        Resolves all TypeAliases into types.
        Cannot be called before all TypeAliases are set.
        Cannot be called before `set_field`.
        '''
        super().resolve()

    def verify_with(self, component_field:VerifyComponentType) -> None:
        '''
        Makes this TypeField verify using this component field when `check` is called.
        :component_field: The ComponentField or OptionalComponentField to check with.
        '''
        self.verify_with_component = component_field

    def get_types(self) -> list[type]:
        '''
        Returns a list of types that this TypeField references.
        Can only be called after `set_field`.
        '''
        ...
