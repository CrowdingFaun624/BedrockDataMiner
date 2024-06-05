from typing import TYPE_CHECKING

import Structure.Importer.Field.ComponentField as ComponentField
import Structure.Importer.Pattern as Capabilities
if TYPE_CHECKING:
    import Structure.Importer.StructureComponent as StructureComponent
    import Structure.Structure as Structure

STRUCTURE_COMPONENT_REQUEST_PROPERTIES = Capabilities.Pattern([{"is_structure": True}])

class StructureComponentField(ComponentField.ComponentField["StructureComponent.StructureComponent"]):
    '''A Field that refers to a StructureComponent (but not a GroupComponent).'''

    def __init__(self, subcomponent_str:str, path: list[str|int], pattern:Capabilities.Pattern=STRUCTURE_COMPONENT_REQUEST_PROPERTIES) -> None:
        '''
        :subcomponent_str: The name of the StructureComponent this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        :pattern: The Pattern to override the default with.
        '''
        super().__init__(subcomponent_str, pattern, path)

    def get_final(self) -> "Structure.Structure":
        '''
        Returns the final Structure that this Field refers to.
        Can only be called after `set_field`.
        '''
        return self.get_component().get_final()
