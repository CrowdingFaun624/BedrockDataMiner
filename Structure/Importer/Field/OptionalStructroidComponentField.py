from typing import TYPE_CHECKING, Union

import Structure.Importer.AbstractGroupComponent as AbstractGroupComponent
import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Field.Field as Field
import Structure.Importer.Field.OptionalComponentField as OptionalComponentField
import Structure.Importer.Pattern as Pattern
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Importer.Component as Component
    import Structure.Importer.StructureComponent as StructureComponent
    import Structure.Structure as Structure

STRUCTROID_COMPONENT_REQUEST_PROPERTIES:Pattern.Pattern[Union["StructureComponent.StructureComponent", "AbstractGroupComponent.AbstractGroupComponent"]] = Pattern.Pattern([{"is_group": True}, {"is_structure": True}])

class OptionalStructroidComponentField(OptionalComponentField.OptionalComponentField[Union["StructureComponent.StructureComponent", "AbstractGroupComponent.AbstractGroupComponent"]]):
    '''A Field that refers to a StructureComponent, an GroupComponent, or no Component.'''

    def __init__(self, subcomponent_data:str|ComponentTyping.StructroidComponentTypedDicts|None, path: list[str|int], pattern:Pattern.Pattern=STRUCTROID_COMPONENT_REQUEST_PROPERTIES, *, allow_in_line:Field.InLinePermissions=Field.InLinePermissions.mixed) -> None:
        '''
        :subcomponent_data: The name of the reference StructureComponent or GroupComponent or the data of the in-line StructureComponent or GroupComponent this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepset, the path through keys/indexes to get to this value.
        :pattern: The Pattern to override the default with.
        :allow_in_line: An InLinePermissions object describing the type of subcomponent_data allowed.
        '''
        super().__init__(subcomponent_data, pattern, path, allow_in_line=allow_in_line)

    def check(self, source_component:"Component.Component") -> list[Exception]:
        exceptions = super().check(source_component)
        if isinstance(self.subcomponent, AbstractGroupComponent.AbstractGroupComponent):
            for subsubcomponent in self.subcomponent.get_subcomponents():
                if subsubcomponent.my_capabilities not in self.pattern:
                    exceptions.append(Exceptions.InvalidComponentError(subsubcomponent, source_component, self.pattern, subsubcomponent.my_capabilities))
        return exceptions

    def get_final(self) -> Union["Structure.Structure", dict[type, Union["Structure.Structure", None]], None]:
        '''
        Returns the final Structure that this Field refers to.
        Can only be called after `set_field`.
        '''
        component = self.get_component()
        if component is None:
            return component
        return component.get_final()
