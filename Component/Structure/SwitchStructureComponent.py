from typing import Sequence

from Component.Capabilities import Capabilities
from Component.ComponentTyping import SwitchStructureTypedDict
from Component.Field.ComponentField import ComponentField
from Component.Field.Field import Field
from Component.Field.FieldListField import FieldListField
from Component.Structure.Field.KeyField import KeyField
from Component.Structure.Field.KeysImportField import KeysImportField
from Component.Structure.FunctionComponent import FUNCTION_PATTERN, FunctionComponent
from Component.Structure.PassthroughStructureComponent import (
    PassthroughStructureComponent,
)
from Structure.StructureTypes.SwitchStructure import SwitchStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    DictTypeVerifier,
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class SwitchStructureComponent(PassthroughStructureComponent[SwitchStructure]):

    __slots__ = (
        "import_field",
        "subcomponents_field",
        "switch_function_field",
    )

    my_capabilities = Capabilities(is_structure=True, has_importable_keys=True)
    class_name = "Switch"
    structure_type = SwitchStructure
    type_verifier = PassthroughStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("imports", False, UnionTypeVerifier(str, dict, ListTypeVerifier((str, dict), list))),
        TypedDictKeyTypeVerifier("switch_function", True, (str, dict)),
        TypedDictKeyTypeVerifier("substructures", True, DictTypeVerifier(dict, str, KeyField.type_verifier)),
    ))

    def initialize_fields(self, data: SwitchStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.switch_function_field = ComponentField(data["switch_function"], FUNCTION_PATTERN, ("switch_function",), assume_type=FunctionComponent.class_name)
        self.subcomponents_field = FieldListField([
            KeyField(key_data, key, self.children_tags, self, (key,), ("substructures", key))
                .add_tag_fields(self.tags_field)
                .add_to_type_set(self.my_type)
            for key, key_data in data.get("substructures", {}).items()
        ], ("substructures",))
        self.import_field = KeysImportField(data.get("imports", ()), ("imports",)).import_into(self.subcomponents_field)

        fields.extend((self.switch_function_field, self.subcomponents_field, self.import_field))
        return fields

    def get_keys(self) -> FieldListField[KeyField]:
        return self.subcomponents_field

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_switch_structure(
            switch_function=self.switch_function_field.subcomponent.final,
            structures={key_field.key: key_field.structure_field.map(lambda component: component.final) for key_field in self.subcomponents_field},
            tags={key.key: tags for key in self.subcomponents_field if len(tags := set(key.tags_field.map(lambda subcomponent: subcomponent.final))) != 0},
            types={key_field.key: key_field.types_field.types for key_field in self.subcomponents_field},
        )
