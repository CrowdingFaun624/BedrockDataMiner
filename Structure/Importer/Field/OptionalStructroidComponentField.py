from typing import TYPE_CHECKING, Union

import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.Field.OptionalComponentField as OptionalComponentField

if TYPE_CHECKING:
    import Structure.Importer.AbstractGroupComponent as AbstractGroupComponent
    import Structure.Importer.StructureComponent as StructureComponent
    import Structure.Structure as Structure

STRUCTUROID_COMPONENT_REQUEST_PROPERTIES:ComponentCapabilities.CapabilitiesPattern[Union["StructureComponent.StructureComponent", "AbstractGroupComponent.AbstractGroupComponent"]] = ComponentCapabilities.CapabilitiesPattern([{"is_group": True}, {"is_structure": True}])

class OptionalStructroidComponentField(OptionalComponentField.OptionalComponentField[Union["StructureComponent.StructureComponent", "AbstractGroupComponent.AbstractGroupComponent"]]):
    '''A Field that refers to a StructureComponent, an GroupComponent, or no Component.'''

    def __init__(self, subcomponent_str:str|None, path: list[str|int], capabilities_pattern:ComponentCapabilities.CapabilitiesPattern=STRUCTUROID_COMPONENT_REQUEST_PROPERTIES) -> None:
        '''
        :subcomponent_str: The name of the StructureComponent this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        :capabilities_pattern: The CapabilitiesPattern to override the default with.
        '''
        super().__init__(subcomponent_str, capabilities_pattern, path)

    def get_final(self) -> Union["Structure.Structure", dict[type, Union["Structure.Structure", None]], None]:
        '''
        Returns the final Structure that this Field refers to.
        Can only be called after `set_field`.
        '''
        component = self.get_component()
        if component is None:
            return component
        structure = component.final
        if structure is None:
            raise RuntimeError("Final Structure of StructureComponent is None!")
        if isinstance(structure, dict):
            null_substructures = [substructure_type for substructure_type, substructure in structure.items() if substructure is None]
            if len(null_substructures) > 0:
                raise RuntimeError("StructroidComponentField cannot accept Groups with substructure of null! Offenders are [%s]" % (", ".join(substructure_type.__name__ for substructure_type in null_substructures)))
        return structure
