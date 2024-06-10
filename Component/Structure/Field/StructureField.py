from typing import TYPE_CHECKING, Callable

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Component as Component
    import Component.Structure.BaseComponent as BaseComponent
    import Structure.StructureBase as StructureBase

STRUCTURE_BASE_REQUEST_PROPERTIES:Pattern.Pattern["BaseComponent.BaseComponent"] = Pattern.Pattern([{"is_base": True}])

class StructureField(ComponentField.ComponentField["BaseComponent.BaseComponent"]):

    def __init__(self, structure_str:str, path:list[str|int], *, assume_type:str|None=None) -> None:
        '''
        :structure_str: The name of the Structure referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        :assume_type: String to use as the type of an inline Component if the type key is missing from it.
        '''
        super().__init__(structure_str, STRUCTURE_BASE_REQUEST_PROPERTIES, path, allow_inline=Field.InLinePermissions.reference, assume_type=assume_type)

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["BaseComponent.BaseComponent"],list["BaseComponent.BaseComponent"]]:
        if not isinstance(self.subcomponent_data, str):
            raise Exceptions.InLineComponentError(source_component, self, self.subcomponent_data)
        structure_component_group = imported_components.get(self.subcomponent_data)
        if structure_component_group is None:
            raise Exceptions.UnrecognizedStructureError(self.subcomponent_data, source_component)

        self.subcomponent, is_inline = Field.choose_component(None, source_component, self.pattern, structure_component_group, {}, self.error_path, create_component_function, self.assume_type)
        self.has_reference_components = self.has_reference_components or not is_inline
        self.has_inline_components = self.has_inline_components or is_inline
        return [self.subcomponent], ([self.subcomponent] if is_inline else [])

    def get_final(self) -> "StructureBase.StructureBase":
        return self.get_component().get_final()
