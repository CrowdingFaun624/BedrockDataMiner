from typing import TYPE_CHECKING, Union

import Structure.Importer.ComponentCapabilities as ComponentCapabilities
import Structure.Importer.Field.OptionalComponentField as OptionalComponentField

if TYPE_CHECKING:
    import Structure.Importer.StructureComponent as StructureComponent
    import Structure.Structure as Structure

STRUCTURE_COMPONENT_REQUEST_PROPERTIES = ComponentCapabilities.CapabilitiesPattern([{"is_structure": True}])

class OptionalStructureComponentField(OptionalComponentField.OptionalComponentField["StructureComponent.StructureComponent"]):
    '''A Field that refers to a StructureComponent (but not a GroupComponent) or no Component.'''

    def __init__(self, subcomponent_str:str|None, path: list[str|int], capabilities_pattern:ComponentCapabilities.CapabilitiesPattern=STRUCTURE_COMPONENT_REQUEST_PROPERTIES) -> None:
        '''
        :subcomponent_str: The name of the StructureComponent this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        :capabilities_pattern: The CapabilitiesPattern to override the default with.
        '''
        super().__init__(subcomponent_str, capabilities_pattern, path)

    def get_final(self) -> Union["Structure.Structure", None]:
        '''
        Returns the final Structure that this Field refers to.
        Can only be called after `set_field`.
        '''
        component = self.get_component()
        if component is None:
            return component
        if component.final is None:
            raise RuntimeError("Final Structure of StructureComponent is None!")
        return component.final
