from typing import TYPE_CHECKING, Callable

import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentGroupField as ComponentGroupField
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Component as Component
    import Component.Structure.BaseComponent as BaseComponent
    import Structure.StructureBase as StructureBase

STRUCTURE_BASE_PATTERN:Pattern.Pattern["BaseComponent.BaseComponent"] = Pattern.Pattern([{"is_base": True}])

class StructureField(ComponentGroupField.ComponentGroupField["BaseComponent.BaseComponent"]):

    __slots__ = (
        "subcomponent",
    )

    def __init__(self, structure_str:str, path:list[str|int]) -> None:
        '''
        :structure_str: The name of the Structure referenced by this Field.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(structure_str, path)
        self.subcomponent:BaseComponent.BaseComponent|None = None

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["BaseComponent.BaseComponent"],list["BaseComponent.BaseComponent"]]:
        super().set_field(source_component, components, imported_components, functions, create_component_function)
        self.subcomponent, is_inline = Field.choose_component(None, source_component, STRUCTURE_BASE_PATTERN, self.get_component_group(), {}, self.error_path, create_component_function, None)
        return [self.subcomponent], []

    def get_component(self) -> "BaseComponent.BaseComponent":
        if self.subcomponent is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.get_component, self)
        return self.subcomponent

    def get_final(self) -> "StructureBase.StructureBase":
        return self.get_component().get_final()
