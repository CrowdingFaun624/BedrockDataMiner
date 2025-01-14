from typing import TYPE_CHECKING, cast

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.ScriptImporter as ScriptImporter
import Component.Structure.Field.AbstractTypeField as AbstractTypeField
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Component as Component
    import Component.Structure.TypeAliasComponent as TypeAliasComponent

TYPE_ALIAS_PATTERN:Pattern.Pattern["TypeAliasComponent.TypeAliasComponent"] = Pattern.Pattern("is_type_alias")

class TypeField(AbstractTypeField.AbstractTypeField):
    '''A link to a TypeAliasComponent or type.'''

    __slots__ = (
        "subcomponent",
        "subcomponent_data",
        "types",
    )

    def __init__(self, subcomponent_data:str, path:list[str|int]) -> None:
        '''
        :subcomponent_data: String representing a default type or Component.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.subcomponent_data = subcomponent_data
        self.subcomponent:type|TypeAliasComponent.TypeAliasComponent

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["TypeAliasComponent.TypeAliasComponent"],list["TypeAliasComponent.TypeAliasComponent"]]:
        if self.subcomponent_data in self.domain.type_stuff.default_types:
            self.subcomponent = self.domain.type_stuff.default_types[self.subcomponent_data]
            return [], []
        else:
            component, is_inline = Field.choose_component(self.subcomponent_data, source_component, TYPE_ALIAS_PATTERN, components, global_components, self.error_path, create_component_function, None, None)
            if is_inline:
                raise Exceptions.InlineComponentError(source_component, self, cast(ComponentTyping.TypeAliasTypedDict, self.subcomponent_data))
            self.subcomponent = component
            return [component], []

    def resolve_link_finals(self) -> None:
        self.types = (self.subcomponent,) if isinstance(self.subcomponent, type) else self.subcomponent.final
