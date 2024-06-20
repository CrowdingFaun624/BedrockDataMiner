from typing import TYPE_CHECKING, TypeAlias

import Component.Field.Field as Field
import Component.Structure.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Component.Structure.Field.StructureComponentField as StructureComponentField
import Component.Structure.StructureComponent as StructureComponent
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Component as Component

VerifyComponentType:TypeAlias = StructureComponentField.StructureComponentField|OptionalStructureComponentField.OptionalStructureComponentField

class AbstractTypeField(Field.Field):

    def __init__(self, path: list[str | int]) -> None:
        super().__init__(path)
        self.verify_with_component:VerifyComponentType|None=None
        self.must_be_types:set[type]|None = None
        self.contained_by_field:AbstractTypeField|None = None

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
        if self.must_be_types is not None:
            for type in self.get_types():
                if type not in self.must_be_types:
                    exceptions.append(Exceptions.ComponentTypeInvalidTypeError(source_component, type, self.must_be_types))
        if self.contained_by_field is not None:
            component_types = self.get_types()
            for supercomponent_type in self.contained_by_field.get_types():
                containment_types = StructureComponent.CONTAINMENT_TYPES.get(supercomponent_type)
                if containment_types is None:
                    continue # the container gives no hints as to what should be contained within it.
                for component_type in component_types:
                    if component_type not in containment_types:
                        exceptions.append(Exceptions.ComponentTypeContainmentError(source_component, supercomponent_type, component_type))
        return exceptions

    def resolve_link_finals(self) -> None:
        '''
        Resolves all TypeAliases into types.
        Cannot be called before all TypeAliases are set.
        Cannot be called before `set_field`.
        '''
        super().resolve_link_finals()

    def verify_with(self, component_field:VerifyComponentType) -> None:
        '''
        Makes this TypeField verify using this component field when `check` is called.
        :component_field: The ComponentField or OptionalComponentField to check with.
        '''
        self.verify_with_component = component_field

    def must_be(self, types:set[type]) -> None:
        '''
        Makes this TypeField check that all of its types are a member of `types`.
        :types: The tuple of types that this TypeField must be.
        '''
        self.must_be_types = types

    def contained_by(self, type_field:"AbstractTypeField") -> None:
        '''
        Makes this TypeField check that its types are those that can be contained by the types in `type_field`.
        :type_field: The TypeField of types that contain this TypeField's types.
        '''
        self.contained_by_field = type_field

    def get_types(self) -> list[type]:
        '''
        Returns a list of types that this TypeField references.
        Can only be called after `set_field`.
        '''
        ...
