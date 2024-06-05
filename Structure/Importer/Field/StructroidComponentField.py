from typing import TYPE_CHECKING, Union

import Structure.Importer.AbstractGroupComponent as AbstractGroupComponent
import Structure.Importer.Field.ComponentField as ComponentField
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.Importer.Pattern as Capabilities
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Importer.StructureComponent as StructureComponent
    import Structure.Structure as Structure

STRUCTUROID_COMPONENT_REQUEST_PROPERTIES:Capabilities.Pattern[Union["StructureComponent.StructureComponent[Structure.Structure]", "AbstractGroupComponent.AbstractGroupComponent"]] = Capabilities.Pattern([{"is_group": True}, {"is_structure": True}])

class StructroidComponentField(ComponentField.ComponentField[Union["StructureComponent.StructureComponent[Structure.Structure]", "AbstractGroupComponent.AbstractGroupComponent"]]):
    '''A Field that refers to a StructureComponent or an GroupComponent.'''

    def __init__(self, subcomponent_str:str, path: list[str|int], pattern:Capabilities.Pattern=STRUCTUROID_COMPONENT_REQUEST_PROPERTIES) -> None:
        '''
        :subcomponent_str: The name of the StructureComponent this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        :pattern: The Pattern to override the default with.
        '''
        super().__init__(subcomponent_str, pattern, path)

    def check(self, component_name: str, component_class_name: str, config: ImporterConfig.ImporterConfig) -> list[Exception]:
        exceptions = super().check(component_name, component_class_name, config)
        if isinstance(self.subcomponent, AbstractGroupComponent.AbstractGroupComponent):
            for subsubcomponent in self.subcomponent.get_subcomponents():
                if subsubcomponent.my_capabilities not in self.pattern:
                    exceptions.append(Exceptions.InvalidComponentError(subsubcomponent, "%s \"%s\"" % (component_class_name, component_name), self.pattern, subsubcomponent.my_capabilities))
        return exceptions

    def get_final(self) -> Union["Structure.Structure", dict[type, "Structure.Structure"]]:
        '''
        Returns the final Structure that this Field refers to.
        Can only be called after `set_field`.
        '''
        structure = self.get_component().get_final()
        if isinstance(structure, dict):
            null_substructures = [substructure_type for substructure_type, substructure in structure.items() if substructure is None]
            if len(null_substructures) > 0:
                raise Exceptions.GroupContainsNullSubcomponentsError(null_substructures, self)
        return structure # type: ignore
