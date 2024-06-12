from typing import TYPE_CHECKING, Callable, cast

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Structure.Field.AbstractTypeField as AbstractTypeField
import Component.Structure.StructureComponent as StructureComponent
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Component as Component
    import Component.Structure.TypeAliasComponent as TypeAliasComponent

TYPE_ALIAS_PATTERN:Pattern.Pattern["TypeAliasComponent.TypeAliasComponent"] = Pattern.Pattern([{"is_type_alias": True}])

class TypeField(AbstractTypeField.AbstractTypeField):
    '''A link to a TypeAliasComponent or type.'''

    def __init__(self, subcomponent_data:str, path:list[str|int]) -> None:
        '''
        :subcomponent_data: String representing a default type or Component.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.subcomponent_data = subcomponent_data
        self.subcomponent:type|TypeAliasComponent.TypeAliasComponent|None = None
        self.types:list[type]|None = None

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["TypeAliasComponent.TypeAliasComponent"],list["TypeAliasComponent.TypeAliasComponent"]]:
        if self.subcomponent_data in StructureComponent.DEFAULT_TYPES:
            self.subcomponent = StructureComponent.DEFAULT_TYPES[self.subcomponent_data]
            return [], []
        else:
            component, is_inline = Field.choose_component(self.subcomponent_data, source_component, TYPE_ALIAS_PATTERN, components, imported_components, self.error_path, create_component_function, None)
            if is_inline:
                raise Exceptions.InLineComponentError(source_component, self, cast(ComponentTyping.TypeAliasTypedDict, self.subcomponent_data))
            self.subcomponent = component
            return [component], []

    def resolve(self) -> None:
        if self.subcomponent is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.resolve, self)
        if isinstance(self.subcomponent, type):
            self.types = [self.subcomponent]
        else:
            self.types = self.subcomponent.get_final()

    def get_types(self) -> list[type]:
        if self.types is None:
            raise Exceptions.FieldSequenceBreakError(self.resolve, self.get_types, self)
        return self.types
