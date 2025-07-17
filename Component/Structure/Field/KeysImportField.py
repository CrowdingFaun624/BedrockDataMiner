from typing import TYPE_CHECKING, Mapping, Self, Sequence

from Component.Component import Component
from Component.ComponentTyping import CreateComponentFunction
from Component.Field.ComponentListField import ComponentListField
from Component.Field.FieldListField import FieldListField
from Component.Pattern import Pattern
from Component.ScriptImporter import ScriptSetSetSet
from Component.Structure.Field.KeyField import KeyField
from Component.Structure.StructureComponent import StructureComponent
from Utilities.Trace import Trace

if TYPE_CHECKING:
    from Component.Group import Group
    from Component.Structure.KeymapStructureComponent import KeymapStructureComponent
    from Component.Structure.SwitchStructureComponent import SwitchStructureComponent

# I tried doing this with Protocols, but there's no way to make a Protocol that is also a subclass of StructureComponent
IMPORTABLE_KEYS_PATTERN:Pattern["KeymapStructureComponent|SwitchStructureComponent"] = Pattern("has_importable_keys")

class KeysImportField(ComponentListField["KeymapStructureComponent|SwitchStructureComponent"]):

    __slots__ = (
        "import_into_keys",
    )

    def __init__(self, subcomponents_data:Sequence[str]|str, path:tuple[str,...], cumulative_path:tuple[str,...]|None=None) -> None:
        '''
        :subcomponents_data: The names of the Components this Field refers to.
        :path: The keys from the next parent Field.
        :cumulative_path: The keys from the next parent Component.
        '''
        super().__init__(subcomponents_data, IMPORTABLE_KEYS_PATTERN, path, cumulative_path)
        self.import_into_keys:FieldListField[KeyField]

    def set_field(
        self,
        source_component:"Component",
        local_group:"Group",
        global_groups:Mapping[str,Mapping[str,"Group"]],
        functions:"ScriptSetSetSet",
        create_component_function:CreateComponentFunction,
        trace:Trace,
    ) -> tuple[Sequence["StructureComponent"],Sequence["StructureComponent"]]:
        with trace.enter_keys(self.trace_path, self.subcomponents_data):
            subcomponents, inline_components = super().set_field(source_component, local_group, global_groups, functions, create_component_function, trace)
            self.import_into_keys.extend(
                key
                for component in subcomponents
                for key in component.get_keys()
                if key.source_component is component
            )
            return subcomponents, inline_components
        return (), ()

    def import_into(self, keys:FieldListField[KeyField]) -> Self:
        '''
        Makes this KeysImportField add keys from other KeymapComponents into the given FieldListField.
        Must call this function before `set_field`.
        :keys: The FieldListField of KeyFields to add into.
        '''
        self.import_into_keys = keys
        return self
