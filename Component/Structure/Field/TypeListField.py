from typing import cast

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.Field as Field
import Component.Pattern as Pattern
import Component.ScriptImporter as ScriptImporter
import Component.Structure.Field.AbstractTypeField as AbstractTypeField
import Component.Structure.TypeAliasComponent as TypeAliasComponent
import Utilities.Exceptions as Exceptions

TYPE_ALIAS_PATTERN:Pattern.Pattern[TypeAliasComponent.TypeAliasComponent] = Pattern.Pattern("is_type_alias")

class TypeListField(AbstractTypeField.AbstractTypeField):
    '''A link to multiple TypeAliasComponents and/or types.'''

    __slots__ = (
        "primitive_types",
        "subcomponents_strs",
        "type_aliases",
        "types",
    )

    def __init__(self, subcomponents_strs:list[str]|str, path:list[str|int]) -> None:
        '''
        :subcomponents_strs: List of string representing a default type or Component.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(path)
        self.subcomponents_strs = [subcomponents_strs] if isinstance(subcomponents_strs, str) else subcomponents_strs
        self.primitive_types:list[type]
        self.type_aliases:list[TypeAliasComponent.TypeAliasComponent]

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["TypeAliasComponent.TypeAliasComponent"],list["TypeAliasComponent.TypeAliasComponent"]]:
        components_used:list["TypeAliasComponent.TypeAliasComponent"] = []
        self.primitive_types = []
        self.type_aliases = []
        already_types:set[str] = set()
        for subcomponent_data in self.subcomponents_strs:
            if subcomponent_data in already_types:
                raise Exceptions.ComponentDuplicateTypeError(subcomponent_data, self, f"(referenced in {Field.get_keys_strs(False, self.error_path)}of {source_component})")
            already_types.add(subcomponent_data)
            if subcomponent_data in self.domain.type_stuff.default_types:
                subcomponent_type = self.domain.type_stuff.default_types[subcomponent_data]
                self.primitive_types.append(subcomponent_type)
            else:
                subcomponent, is_inline = Field.choose_component(subcomponent_data, source_component, TYPE_ALIAS_PATTERN, components, global_components, self.error_path, create_component_function, None, None)
                if is_inline:
                    raise Exceptions.InlineComponentError(source_component, self, cast(ComponentTyping.TypeAliasTypedDict, subcomponent_data))
                components_used.append(subcomponent)
                self.type_aliases.append(subcomponent)
        return components_used, []

    def resolve_link_finals(self) -> None:
        types:list[type] = []
        types.extend(self.primitive_types)
        for type_alias_component in self.type_aliases:
            types.extend(type_alias_component.final)
        self.types = tuple(types)

    def __len__(self) -> int:
        return len(self.types)
