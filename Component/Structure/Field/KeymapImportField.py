from typing import TYPE_CHECKING, Self, Sequence

import Component.Structure.KeymapStructureComponent as KeymapStructureComponent  # import loop
from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction
from Component.Field.ComponentListField import ComponentListField
from Component.Field.Field import InlinePermissions
from Component.Field.FieldListField import FieldListField
from Component.ScriptImporter import ScriptSetSetSet
from Component.Structure.Field.KeymapKeyField import KeymapKeyField
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group

class KeymapImportField(ComponentListField["KeymapStructureComponent.KeymapStructureComponent"]):

    __slots__ = (
        "import_into_keys",
    )

    def __init__(self, subcomponents_data:Sequence[str]|str, path:tuple[str,...], cumulative_path:tuple[str,...]|None=None) -> None:
        '''
        :subcomponents_data: The names of the Components this Field refers to.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        '''
        super().__init__(subcomponents_data, KeymapStructureComponent.IMPORTABLE_KEYS_PATTERN, path, cumulative_path, allow_inline=InlinePermissions.reference)
        self.import_into_keys:FieldListField[KeymapKeyField]

    def set_field(
        self,
        source_component:"Component",
        local_group:"Group",
        global_groups:dict[str,dict[str,"Group"]],
        functions:"ScriptSetSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["KeymapStructureComponent.KeymapStructureComponent"],Sequence["KeymapStructureComponent.KeymapStructureComponent"]]:
        with trace.enter_keys(self.trace_path, self.subcomponents_data):
            subcomponents, inline_components = super().set_field(source_component, local_group, global_groups, functions, create_component_function, trace)
            self.import_into_keys.extend(
                key
                for component in subcomponents
                for key in component.keys
                if key.source_component is component
            )
            return subcomponents, inline_components
        return (), ()

    def import_into(self, keys:FieldListField[KeymapKeyField]) -> Self:
        '''
        Makes this KeymapImportField add keys from other KeymapComponents into the given FieldListField.
        Must call this function before `set_field`.
        :keys: The FieldListField of KeymapKeyFields to add into.
        '''
        self.import_into_keys = keys
        return self
