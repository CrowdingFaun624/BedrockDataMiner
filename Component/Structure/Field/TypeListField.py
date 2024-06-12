from typing import TYPE_CHECKING, Callable, cast

import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.Structure.Field.AbstractTypeField as AbstractTypeField
import Component.Structure.StructureComponent as StructureComponent
import Component.Structure.TypeAliasComponent as TypeAliasComponent
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Component as Component

TYPE_ALIAS_PATTERN:Pattern.Pattern[TypeAliasComponent.TypeAliasComponent] = Pattern.Pattern([{"is_type_alias": True}])

class TypeListField(AbstractTypeField.AbstractTypeField):
    '''A link to multiple TypeAliasComponents and/or types.'''

    def __init__(self, subcomponents_strs:list[str]|str, path:list[str|int]) -> None:
        '''
        :subcomponents_strs: List of string representing a default type or Component.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.subcomponents_strs = [subcomponents_strs] if isinstance(subcomponents_strs, str) else subcomponents_strs
        self.primitive_types:list[type]|None = None
        self.type_aliases:list[TypeAliasComponent.TypeAliasComponent]|None = None
        self.types:list[type]|None = None

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["TypeAliasComponent.TypeAliasComponent"],list["TypeAliasComponent.TypeAliasComponent"]]:
        components_used:list["TypeAliasComponent.TypeAliasComponent"] = []
        self.primitive_types = []
        self.type_aliases = []
        already_types:set[str] = set()
        for subcomponent_data in self.subcomponents_strs:
            if subcomponent_data in already_types:
                raise Exceptions.ComponentDuplicateTypeError(subcomponent_data, self, "(referenced in %sof %r)" % (Field.get_keys_strs(False, self.error_path), source_component))
            already_types.add(subcomponent_data)
            if subcomponent_data in StructureComponent.DEFAULT_TYPES:
                subcomponent_type = StructureComponent.DEFAULT_TYPES[subcomponent_data]
                self.primitive_types.append(subcomponent_type)
            else:
                subcomponent, is_inline = Field.choose_component(subcomponent_data, source_component, TYPE_ALIAS_PATTERN, components, imported_components, self.error_path, create_component_function, None)
                if is_inline:
                    raise Exceptions.InLineComponentError(source_component, self, cast(ComponentTyping.TypeAliasTypedDict, subcomponent_data))
                components_used.append(subcomponent)
                self.type_aliases.append(subcomponent)
        return components_used, []

    def resolve(self) -> None:
        if self.primitive_types is None or self.type_aliases is None:
            raise Exceptions.FieldSequenceBreakError(self.set_field, self.resolve, self)
        self.types = []
        self.types.extend(self.primitive_types)
        for type_alias_component in self.type_aliases:
            self.types.extend(type_alias_component.get_final())

    def get_types(self) -> list[type]:
        if self.types is None:
            raise Exceptions.FieldSequenceBreakError(self.resolve, self.get_types, self)
        return self.types
