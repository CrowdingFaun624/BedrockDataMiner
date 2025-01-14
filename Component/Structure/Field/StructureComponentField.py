import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Structure.StructureComponent as StructureComponent

STRUCTURE_COMPONENT_PATTERN = Pattern.Pattern("is_structure")

class StructureComponentField(ComponentField.ComponentField["StructureComponent.StructureComponent"]):
    '''A Field that refers to a StructureComponent (but not a GroupComponent).'''

    __slots__ = ()

    def __init__(self, subcomponent_data:str|ComponentTyping.StructureTypedDicts, path: list[str|int], pattern:Pattern.Pattern=STRUCTURE_COMPONENT_PATTERN, *, allow_inline:Field.InlinePermissions=Field.InlinePermissions.mixed) -> None:
        '''
        :subcomponent_data: The name of the reference StructureComponent or the data of the inline StructureComponent this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :pattern: The Pattern to override the default with.
        :allow_inline: An InlinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__(subcomponent_data, pattern, path, allow_inline=allow_inline)
