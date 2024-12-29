from typing import Callable

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Pattern as Pattern
import Component.Structure.Field.KeymapKeyField as KeymapKeyField
import Component.Structure.KeymapComponent as KeymapComponent
import Utilities.Exceptions as Exceptions

IMPORTABLE_KEYS_PATTERN:Pattern.Pattern["KeymapComponent.KeymapComponent"] = Pattern.Pattern([{"has_importable_keys": True}])

class KeymapImportField(ComponentListField.ComponentListField["KeymapComponent.KeymapComponent"]):

    __slots__ = (
        "import_into_keys",
    )

    def __init__(self, subcomponents_data:list[str]|str, path:list[str|int]) -> None:
        '''
        :subcomponents_data: The names of the Components this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(subcomponents_data, IMPORTABLE_KEYS_PATTERN, path, allow_inline=Field.InlinePermissions.reference)
        self.import_into_keys:FieldListField.FieldListField[KeymapKeyField.KeymapKeyField]|None = None

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["KeymapComponent.KeymapComponent"],list["KeymapComponent.KeymapComponent"]]:
        subcomponents, inline_components = super().set_field(source_component, components, imported_components, functions, create_component_function)
        if self.import_into_keys is None:
            raise Exceptions.FieldSequenceBreakError(self.import_into, self.set_field, self)
        self.import_into_keys.extend(
            key
            for component in subcomponents
            for key in component.keys
            if key.source_component is component
        )
        return subcomponents, inline_components

    def import_into(self, keys:FieldListField.FieldListField[KeymapKeyField.KeymapKeyField]) -> None:
        '''
        Makes this KeymapImportField add keys from other KeymapComponents into the given FieldListField.
        Must call this function before `set_field`.
        :keys: The FieldListField of KeymapKeyFields to add into.
        '''
        self.import_into_keys = keys
