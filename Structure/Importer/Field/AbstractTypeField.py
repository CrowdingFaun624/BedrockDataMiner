from typing import TypeAlias

import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.Field as Field
import Structure.Importer.Field.OptionalStructroidComponentField as OptionalStructroidComponentField
import Structure.Importer.Field.OptionalStructureComponentField as OptionalStructureComponentField
import Structure.Importer.Field.StructroidComponentField as StructroidComponentField
import Structure.Importer.Field.StructureComponentField as StructureComponentField
import Structure.Importer.ImporterConfig as ImporterConfig

VerifyComponentType:TypeAlias = StructroidComponentField.StructroidComponentField|OptionalStructroidComponentField.OptionalStructroidComponentField|StructureComponentField.StructureComponentField|OptionalStructureComponentField.OptionalStructureComponentField

class AbstractTypeField(Field.Field):

    def __init__(self, path: list[str | int]) -> None:
        super().__init__(path)
        self.verify_with_component:VerifyComponentType|None=None

    def check(self, component_name: str, component_class_name: str, config: ImporterConfig.ImporterConfig) -> list[Exception]:
        exceptions = super().check(component_name, component_class_name, config)
        if self.verify_with_component is not None:
            subcomponent = self.verify_with_component.get_component()
            component_types = self.get_types()
            if subcomponent is None:
                for value_type in component_types:
                    if value_type in ComponentTyping.REQUIRES_SUBCOMPONENT_TYPES:
                        exceptions.append(TypeError("%s \"%s\" accepts type %s, but has a null Subcomponent!" % (component_class_name, component_name, value_type.__name__)))
            else:
                if set(component_types) != set(subcomponent.my_type):
                    my_types = ", ".join(type_item.__name__ for type_item in component_types)
                    its_types = ", ".join(type_item.__name__ for type_item in subcomponent.my_type)
                    exceptions.append(TypeError("%s \"%s\" accepts types [%s], but its Subcomponent, \"%s\", only accepts type [%s]!" % (component_class_name, component_name, my_types, subcomponent.name, its_types)))
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