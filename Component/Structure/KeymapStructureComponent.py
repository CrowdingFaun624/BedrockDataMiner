from typing import Sequence

import Component.Capabilities as Capabilities
import Component.ComponentTyping as ComponentTyping
import Component.Field.ComponentField as ComponentField
import Component.Field.Field as Field
import Component.Field.FieldListField as FieldListField
import Component.Pattern as Pattern
import Component.Structure.Field.KeymapImportField as KeymapImportField
import Component.Structure.Field.KeymapKeyField as KeymapKeyField
import Component.Structure.Field.TagListField as TagListField
import Component.Structure.MappingStructureComponent as MappingStructureComponent
import Component.Structure.StructureComponent as StructureComponent
import Structure.StructureTypes.KeymapStructure as KeymapStructure
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace
import Utilities.TypeVerifier as TypeVerifier

IMPORTABLE_KEYS_PATTERN:Pattern.Pattern["KeymapStructureComponent"] = Pattern.Pattern("has_importable_keys")

class KeymapStructureComponent(MappingStructureComponent.MappingStructureComponent[KeymapStructure.KeymapStructure]):

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
    structure_type = KeymapStructure.KeymapStructure
    my_capabilities = Capabilities.Capabilities(has_importable_keys=True, is_structure=True)
    default_this_types_name = "dict"
    type_verifier = MappingStructureComponent.MappingStructureComponent.type_verifier.extend(TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("allow_key_moves", False, bool),
        TypeVerifier.TypedDictKeyTypeVerifier("imports", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
        TypeVerifier.TypedDictKeyTypeVerifier("key_structure", False, (str, dict, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("key_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
        TypeVerifier.TypedDictKeyTypeVerifier("keys", False, TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("delegate_arguments", False, dict),
            TypeVerifier.TypedDictKeyTypeVerifier("required", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("similarity_weight", False, int, lambda key, value: (value >= 0, "must be positive")),
            TypeVerifier.TypedDictKeyTypeVerifier("structure", False, (str, dict, type(None))),
            TypeVerifier.TypedDictKeyTypeVerifier("tags", False, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
            TypeVerifier.TypedDictKeyTypeVerifier("types", True, TypeVerifier.UnionTypeVerifier(str, TypeVerifier.ListTypeVerifier(str, list))),
            TypeVerifier.TypedDictKeyTypeVerifier("value_weight", False, (int, type(None)), lambda key, value: (value is None or value >= 0, "must be positive")),
        ))),
        TypeVerifier.TypedDictKeyTypeVerifier("value_weight", False, int),
    ))

    def initialize_fields(self, data: ComponentTyping.KeymapStructureTypedDict) -> Sequence[Field.Field]:
        fields = list(super().initialize_fields(data))

        self.allow_key_moves = data.get("allow_key_moves", False)
        self.key_weight = data.get("key_weight", self.structure_type.KEY_WEIGHT)
        self.value_weight = data.get("value_weight", self.structure_type.VALUE_WEIGHT)

        self.tags_for_all_field = TagListField.TagListField(data.get("tags", ()), ("tags",)).add_to_tag_set(self.children_tags) # must be before keys.
        self.keys = FieldListField.FieldListField([
            KeymapKeyField.KeymapKeyField(key_data, key, self.children_tags, (key,), self).add_tag_fields(self.tags_for_all_field)
            for key, key_data in data.get("keys", {}).items()
        ], ("keys",))
        self.key_structure_field = ComponentField.OptionalComponentField(data.get("key_structure", None), StructureComponent.STRUCTURE_COMPONENT_PATTERN, ("key_structure",))
        self.import_field = KeymapImportField.KeymapImportField(data.get("imports", ()), ("imports",)).import_into(self.keys)
        fields.extend((self.keys, self.key_structure_field, self.import_field, self.tags_for_all_field))
        return fields

    def link_finals(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            self.delegate_keys = {key.key: key.delegate_arguments for key in self.keys}
            super().link_finals(trace)
            self.final.link_keymap_structure(
                allow_key_moves=self.allow_key_moves,
                allow_same_key_optimization=True,
                key_structure=self.key_structure_field.map(lambda subcomponent: subcomponent.final),
                key_weight=self.key_weight,
                similarity_weights={key.key: key.similarity_weight for key in self.keys},
                value_structures={key.key: key.subcomponent_field.map(lambda subcomponent: subcomponent.final) for key in self.keys},
                value_tags={key.key: value_tags for key in self.keys if len(value_tags := set(key.tags_field.map(lambda subcomponent: subcomponent.final))) != 0},
                value_types={key.key: key.types_field.types for key in self.keys},
                value_weights={key.key: key.value_weight if key.value_weight is not None else self.value_weight for key in self.keys},
            )

    def check(self, trace: Trace.Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().check(trace)
            if self.key_weight == 0:
                for key_field in self.keys:
                    if key_field.value_weight == 0:
                        trace.exception(Exceptions.ZeroWeightError("key_weight", f"keys[{key_field.key}][weight]"))
