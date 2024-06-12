from typing import TYPE_CHECKING, Union

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Structure.AbstractGroupComponent as AbstractGroupComponent
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Component as Component
    import Component.Structure.StructureComponent as StructureComponent
    import Structure.Structure as Structure

STRUCTROID_COMPONENT_PATTERN:Pattern.Pattern[Union["StructureComponent.StructureComponent[Structure.Structure]", "AbstractGroupComponent.AbstractGroupComponent"]] = Pattern.Pattern([{"is_group": True}, {"is_structure": True}])

class StructroidComponentField(ComponentField.ComponentField[Union["StructureComponent.StructureComponent[Structure.Structure]", "AbstractGroupComponent.AbstractGroupComponent"]]):
    '''A Field that refers to a StructureComponent or an GroupComponent.'''

    def __init__(self, subcomponent_data:str|ComponentTyping.StructroidComponentTypedDicts, path: list[str|int], pattern:Pattern.Pattern=STRUCTROID_COMPONENT_PATTERN, allow_inline:Field.InLinePermissions=Field.InLinePermissions.mixed) -> None:
        '''
        :subcomponent_data: The name of the reference StructureComponent or GroupComponent or the data of the inline StructureComponent or GroupComponent this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :pattern: The Pattern to override the default with.
        :allow_inline: An InLinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__(subcomponent_data, pattern, path, allow_inline=allow_inline)

    def check(self, source_component:"Component.Component") -> list[Exception]:
        exceptions = super().check(source_component)
        if isinstance(self.subcomponent, AbstractGroupComponent.AbstractGroupComponent):
            for subsubcomponent in self.subcomponent.get_subcomponents():
                if subsubcomponent.my_capabilities not in self.pattern:
                    exceptions.append(Exceptions.InvalidComponentError(subsubcomponent, source_component, self.pattern, subsubcomponent.my_capabilities))
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
