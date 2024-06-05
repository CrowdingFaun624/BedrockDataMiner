from typing import TYPE_CHECKING, Callable, Sequence, cast

import Structure.Importer.Component as Component
import Structure.Importer.Field.ComponentListField as ComponentListField
import Structure.Importer.Field.FieldListField as FieldListField
import Structure.Importer.Field.KeymapKeyField as KeymapKeyField
import Structure.Importer.Pattern as Capabilities
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Importer.KeymapComponent as KeymapComponent

IMPORTABLE_KEYS_REQUEST_PROPERTIES:Capabilities.Pattern["KeymapComponent.KeymapComponent"] = Capabilities.Pattern([{"has_importable_keys": True}])

class KeymapImportField(ComponentListField.ComponentListField):

    def __init__(self, subcomponents_strs:list[str]|str, path:list[str|int]) -> None:
        '''
        :subcomponents_strs: The names of the Components this Field refers to.
        :path: A list of strings and/or integers that represent, in order from shallowest to deepest, the path through keys/indexes to get to this value.
        '''
        super().__init__(subcomponents_strs, IMPORTABLE_KEYS_REQUEST_PROPERTIES, path)
        self.import_into_keys:FieldListField.FieldListField[KeymapKeyField.KeymapKeyField]|None = None
        self.tag_set:set[str]|None = None

    def set_field(self, component_name: str, component_class_name: str, components: dict[str, Component.Component], functions: dict[str, Callable]) -> Sequence[Component.Component]:
        output = cast(Sequence["KeymapComponent.KeymapComponent"], super().set_field(component_name, component_class_name, components, functions))
        if self.import_into_keys is None:
            raise Exceptions.FieldSequenceBreakError(self.import_into, self.set_field, self)
        tag_set = self.tag_set
        for component in output:
            self.import_into_keys.extend(key.copy_for_importing() for key in iter(component.keys) if not key.has_been_imported)
            if tag_set is not None:
                self.import_into_keys.for_each(lambda keymap_key_field: keymap_key_field.add_to_tag_set(tag_set))
        return output

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
