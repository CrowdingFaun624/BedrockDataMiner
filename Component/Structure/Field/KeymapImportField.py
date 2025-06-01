from typing import Self, Sequence

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.ScriptImporter as ScriptImporter
import Component.Structure.Field.KeymapKeyField as KeymapKeyField
import Component.Structure.KeymapStructureComponent as KeymapStructureComponent
import Utilities.Trace as Trace


class KeymapImportField(ComponentListField.ComponentListField["KeymapStructureComponent.KeymapStructureComponent"]):

    __slots__ = (
        "import_into_keys",
    )

    def __init__(self, subcomponents_data:Sequence[str]|str, path:tuple[str,...]) -> None:
        '''
        :subcomponents_data: The names of the Components this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(subcomponents_data, KeymapStructureComponent.IMPORTABLE_KEYS_PATTERN, path, allow_inline=Field.InlinePermissions.reference)
        self.import_into_keys:FieldListField.FieldListField[KeymapKeyField.KeymapKeyField]

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        global_components:dict[str,dict[str,dict[str,"Component.Component"]]],
        functions:ScriptImporter.ScriptSetSetSet,
        create_component_function:ComponentTyping.CreateComponentFunction,
        trace:Trace.Trace,
    ) -> tuple[Sequence["KeymapStructureComponent.KeymapStructureComponent"],Sequence["KeymapStructureComponent.KeymapStructureComponent"]]:
        with trace.enter_keys(self.trace_path, self.subcomponents_data):
            subcomponents, inline_components = super().set_field(source_component, components, global_components, functions, create_component_function, trace)
            self.import_into_keys.extend(
                key
                for component in subcomponents
                for key in component.keys
                if key.source_component is component
            )
            return subcomponents, inline_components
        return (), ()

    def import_into(self, keys:FieldListField.FieldListField[KeymapKeyField.KeymapKeyField]) -> Self:
        '''
        Makes this KeymapImportField add keys from other KeymapComponents into the given FieldListField.
        Must call this function before `set_field`.
        :keys: The FieldListField of KeymapKeyFields to add into.
        '''
        self.import_into_keys = keys
        return self
