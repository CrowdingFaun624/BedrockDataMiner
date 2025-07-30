from typing import Sequence

from Component.Capabilities import Capabilities
from Component.ComponentTyping import KeymapStructureTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field
from Component.Field.FieldListField import FieldListField
from Component.Structure.Field.KeyField import KeyField
from Component.Structure.Field.KeysImportField import KeysImportField
from Component.Structure.Field.TagListField import TagListField
from Component.Structure.MappingStructureComponent import MappingStructureComponent
from Component.Structure.StructureComponent import STRUCTURE_COMPONENT_PATTERN
from Structure.StructureTypes.KeymapStructure import KeymapStructure
from Utilities.Exceptions import ZeroWeightError
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class KeymapStructureComponent(MappingStructureComponent[KeymapStructure]):

    __slots__ = (
        "allow_key_moves",
        "import_field",
        "key_structure_field",
        "key_weight",
        "keys",
        "tags_for_all_field",
        "value_weight",
    )

    class_name = "Keymap"
    structure_type = KeymapStructure
    my_capabilities = Capabilities(has_importable_keys=True, is_structure=True)
    default_this_types_name = "dict"
    type_verifier = MappingStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("allow_key_moves", False, bool),
        TypedDictKeyTypeVerifier("imports", False, UnionTypeVerifier(str, dict, ListTypeVerifier((str, dict), list))),
        TypedDictKeyTypeVerifier("key_structure", False, (str, dict, type(None))),
        TypedDictKeyTypeVerifier("key_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
        TypedDictKeyTypeVerifier("keys", False, DictTypeVerifier(dict, str, KeyField.type_verifier)),
        TypedDictKeyTypeVerifier("value_weight", False, int),
    ))

    def initialize_fields(self, data: KeymapStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.allow_key_moves = data.get("allow_key_moves", False)
        self.key_weight = data.get("key_weight", self.structure_type.KEY_WEIGHT)
        self.value_weight = data.get("value_weight", self.structure_type.VALUE_WEIGHT)

        self.tags_for_all_field = TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags) # must be before keys.
        self.keys = FieldListField([
            KeyField(key_data, key, self.children_tags, self, (key,), ("keys", key)).add_tag_fields(self.tags_for_all_field)
            for key, key_data in data.get("keys", {}).items()
        ], ("keys",))
        self.key_structure_field = OptionalComponentField(data.get("key_structure", None), STRUCTURE_COMPONENT_PATTERN, ("key_structure",))
        self.import_field = KeysImportField(data.get("imports", ()), ("imports",)).import_into(self.keys)
        fields.extend((self.keys, self.key_structure_field, self.import_field, self.tags_for_all_field))
        return fields

    def get_keys(self) -> FieldListField[KeyField]:
        return self.keys

    def link_finals(self, trace: Trace) -> None:
        self.delegate_keys = {key.key: key.delegate_arguments for key in self.keys}
        super().link_finals(trace)
        self.final.link_keymap_structure(
            allow_key_moves=self.allow_key_moves,
            allow_same_key_optimization=True,
            key_structure=self.key_structure_field.map(lambda subcomponent: subcomponent.final),
            key_weight=self.key_weight,
            similarity_weights={key.key: key.similarity_weight for key in self.keys},
            value_structure_origins={key.key: key.source_component.final for key in self.keys},
            value_structures={key.key: key.structure_field.map(lambda subcomponent: subcomponent.final) for key in self.keys},
            value_tags={key.key: value_tags for key in self.keys if len(value_tags := set(key.tags_field.map(lambda subcomponent: subcomponent.final))) != 0},
            value_types={key.key: key.types_field.types for key in self.keys},
            value_weights={key.key: key.value_weight if key.value_weight is not None else self.value_weight for key in self.keys},
        )

    def check(self, trace: Trace) -> None:
        if self.key_weight == 0:
            for key_field in self.keys:
                if key_field.value_weight == 0:
                    trace.exception(ZeroWeightError("key_weight", f"keys[{key_field.key}][weight]"))
