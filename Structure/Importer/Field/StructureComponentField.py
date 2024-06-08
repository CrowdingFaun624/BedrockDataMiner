from typing import TYPE_CHECKING

import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.Field as Field
import Structure.Importer.Field.ComponentField as ComponentField
import Structure.Importer.Pattern as Pattern

if TYPE_CHECKING:
    import Structure.Importer.StructureComponent as StructureComponent
    import Structure.Structure as Structure

STRUCTURE_COMPONENT_REQUEST_PROPERTIES = Pattern.Pattern([{"is_structure": True}])

class StructureComponentField(ComponentField.ComponentField["StructureComponent.StructureComponent"]):
    '''A Field that refers to a StructureComponent (but not a GroupComponent).'''

    def __init__(self, subcomponent_data:str|ComponentTyping.StructureComponentTypedDicts, path: list[str|int], pattern:Pattern.Pattern=STRUCTURE_COMPONENT_REQUEST_PROPERTIES, *, allow_in_line:Field.InLinePermissions=Field.InLinePermissions.mixed) -> None:
        '''
        :subcomponent_data: The name of the reference StructureComponent or the data of the in-line StructureComponent this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        :pattern: The Pattern to override the default with.
        :allow_in_line: An InLinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__(subcomponent_data, pattern, path, allow_in_line=allow_in_line)

    def get_final(self) -> "Structure.Structure":
        '''
        Returns the final Structure that this Field refers to.
        Can only be called after `set_field`.
        '''
        return self.get_component().get_final()
