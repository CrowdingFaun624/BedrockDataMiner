from typing import TYPE_CHECKING, Union

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.OptionalComponentField as OptionalComponentField
import Component.Pattern as Pattern

if TYPE_CHECKING:
    import Component.Structure.StructureComponent as StructureComponent
    import Structure.Structure as Structure

STRUCTURE_COMPONENT_REQUEST_PROPERTIES = Pattern.Pattern([{"is_structure": True}])

class OptionalStructureComponentField(OptionalComponentField.OptionalComponentField["StructureComponent.StructureComponent"]):
    '''A Field that refers to a StructureComponent (but not a GroupComponent) or no Component.'''

    def __init__(self, subcomponent_data:str|ComponentTyping.StructureComponentTypedDicts|None, path: list[str|int], pattern:Pattern.Pattern=STRUCTURE_COMPONENT_REQUEST_PROPERTIES, *, allow_in_line:Field.InLinePermissions=Field.InLinePermissions.mixed) -> None:
        '''
        :subcomponent_data: The name of the reference StructureComponent or the data of the in-line StructureComponent this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        :pattern: The Pattern to override the default with.
        :allow_in_line: An InLinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__(subcomponent_data, pattern, path, allow_in_line=allow_in_line)

    def get_final(self) -> Union["Structure.Structure", None]:
        '''
        Returns the final Structure that this Field refers to.
        Can only be called after `set_field`.
        '''
        component = self.get_component()
        if component is None:
            return component
        return component.get_final()
