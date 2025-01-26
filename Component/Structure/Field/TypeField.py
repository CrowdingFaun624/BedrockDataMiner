from typing import Sequence, cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.ScriptImporter as ScriptImporter
import Component.Structure.Field.AbstractTypeField as AbstractTypeField
import Component.Structure.TypeAliasComponent as TypeAliasComponent
import Utilities.Exceptions as Exceptions


class TypeField(AbstractTypeField.AbstractTypeField):
    '''A link to a TypeAliasComponent or type.'''

    __slots__ = (
        "subcomponent",
        "subcomponent_data",
        "types",
    )

    def __init__(self, subcomponent_data:str, path:tuple[str,...]) -> None:
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
    ) -> tuple[Sequence["TypeAliasComponent.TypeAliasComponent"],Sequence["TypeAliasComponent.TypeAliasComponent"]]:
        if self.subcomponent_data in self.domain.type_stuff.default_types:
            self.subcomponent = self.domain.type_stuff.default_types[self.subcomponent_data]
            return (), ()
        else:
            component, is_inline = Field.choose_component(self.subcomponent_data, source_component, TypeAliasComponent.TYPE_ALIAS_PATTERN, components, global_components, self.error_path, create_component_function, None, None, self.domain.type_stuff.default_types)
            if is_inline:
                raise Exceptions.InlineComponentError(source_component, self, cast(ComponentTyping.TypeAliasTypedDict, self.subcomponent_data))
            self.subcomponent = component
            return (component,), ()

    def resolve_link_finals(self) -> None:
        self.types = (self.subcomponent,) if isinstance(self.subcomponent, type) else self.subcomponent.final
        if self.type_set is not None:
            self.type_set.update(self.types)
