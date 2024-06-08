from typing import TYPE_CHECKING, Callable

import Component.Component as Component
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentListField as ComponentListField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Pattern as Pattern
import Component.Structure.Field.KeymapKeyField as KeymapKeyField
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Component.Structure.KeymapComponent as KeymapComponent

IMPORTABLE_KEYS_REQUEST_PROPERTIES:Pattern.Pattern["KeymapComponent.KeymapComponent"] = Pattern.Pattern([{"has_importable_keys": True}])

class KeymapImportField(ComponentListField.ComponentListField["KeymapComponent.KeymapComponent"]):

    def __init__(self, subcomponents_data:list[str]|str, path:list[str|int]) -> None:
        '''
        :subcomponents_data: The names of the Components this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(subcomponents_data, IMPORTABLE_KEYS_REQUEST_PROPERTIES, path, allow_in_line=Field.InLinePermissions.reference)
        self.import_into_keys:FieldListField.FieldListField[KeymapKeyField.KeymapKeyField]|None = None
        self.tag_set:set[str]|None = None

    def set_field(
        self,
        source_component:"Component.Component",
        components:dict[str,"Component.Component"],
        imported_components:dict[str,dict[str,"Component.Component"]],
        functions:dict[str,Callable],
        create_component_function:ComponentTyping.CreateComponentFunction,
    ) -> tuple[list["KeymapComponent.KeymapComponent"],list["KeymapComponent.KeymapComponent"]]:
        subcomponents, in_line_components = super().set_field(source_component, components, imported_components, functions, create_component_function)
        if self.import_into_keys is None:
            raise Exceptions.FieldSequenceBreakError(self.import_into, self.set_field, self)
        tag_set = self.tag_set
        for component in subcomponents:
            self.import_into_keys.extend(key.copy_for_importing() for key in iter(component.keys) if not key.has_been_imported)
            if tag_set is not None:
                self.import_into_keys.for_each(lambda keymap_key_field: keymap_key_field.add_to_tag_set(tag_set))
        return subcomponents, in_line_components

    def import_into(self, keys:FieldListField.FieldListField[KeymapKeyField.KeymapKeyField]) -> None:
        '''
        Makes this KeymapImportField add keys from other KeymapComponents into the given FieldListField.
        Must call this function before `set_field`.
        :keys: The FieldListField of KeymapKeyFields to add into.
        '''
        self.import_into_keys = keys

    def add_to_tag_set(self, tag_set:set[str]) -> None:
        '''
        Makes this KeymapImportField add tags into the given tag_set when `set_field` is called.
        :tag_set: The set of tag strings to add to.
        '''
        self.tag_set = tag_set
