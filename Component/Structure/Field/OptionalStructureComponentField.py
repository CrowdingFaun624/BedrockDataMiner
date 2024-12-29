from typing import TYPE_CHECKING

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Field.OptionalComponentField as OptionalComponentField
import Component.Pattern as Pattern

if TYPE_CHECKING:
    import Component.Structure.StructureComponent as StructureComponent
    import Structure.Structure as Structure

STRUCTURE_COMPONENT_PATTERN = Pattern.Pattern([{"is_structure": True}])

class OptionalStructureComponentField(OptionalComponentField.OptionalComponentField["StructureComponent.StructureComponent"]):
    '''A Field that refers to a StructureComponent (but not a GroupComponent) or no Component.'''

    __slots__ = ()

    def __init__(self, subcomponent_data:str|ComponentTyping.StructureTypedDicts|None, path: list[str|int], pattern:Pattern.Pattern=STRUCTURE_COMPONENT_PATTERN, *, allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed) -> None:
        '''
        :subcomponent_data: The name of the reference StructureComponent or the data of the inline StructureComponent this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :pattern: The Pattern to override the default with.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__(subcomponent_data, pattern, path, allow_inline=allow_inline)

    def get_final(self) -> "Structure.Structure|None":
        '''
        Returns the final Structure that this Field refers to.
        Can only be called after `set_field`.
        '''
        component = self.get_component()
        if component is None:
            return component
        return component.get_final()
