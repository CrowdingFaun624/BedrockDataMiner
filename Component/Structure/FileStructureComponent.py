from typing import Sequence

from Component.ComponentTyping import FileStructureTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field
from Component.Serializer.SerializerComponent import SERIALIZER_PATTERN
from Component.Structure.Field.TypeListField import TypeListField
from Component.Structure.PassthroughStructureComponent import (
    PassthroughStructureComponent,
)
from Component.Structure.StructureComponent import STRUCTURE_COMPONENT_PATTERN
from Structure.StructureTypes.FileStructure import FileStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)


class FileStructureComponent(PassthroughStructureComponent[FileStructure]):

    __slots__ = (
        "content_types_field",
        "file_types_field",
        "serializer_field",
        "structure_field",
    )

    class_name = "File"
    structure_type = FileStructure
    type_verifier = PassthroughStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("content_types", True, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("file_types", False, UnionTypeVerifier(str, ListTypeVerifier(str, list))),
        TypedDictKeyTypeVerifier("serializer", True, (str, dict, type(None))),
        TypedDictKeyTypeVerifier("structure", True, (str, dict, type(None))),
    ))

    def initialize_fields(self, data: FileStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.file_types_field = TypeListField(data.get("file_types", "abstract_file"), ("file_types",)).must_be(self.domain.type_stuff.file_types).make_default(self.pre_normalized_types_field)
        self.structure_field = OptionalComponentField(data["structure"], STRUCTURE_COMPONENT_PATTERN, ("structure",))
        self.content_types_field = TypeListField(data["content_types"], ("content_types",)).verify_with(self.structure_field).add_to_set(self.my_type)
        self.serializer_field = OptionalComponentField(data["serializer"], SERIALIZER_PATTERN, ("serializer",), assume_component_group="serializers")

        fields.extend((self.file_types_field, self.structure_field, self.content_types_field, self.serializer_field))
        return fields

    def link_finals(self, trace: Trace) -> None:
        with trace.enter(self, self.name, ...):
            super().link_finals(trace)
            self.final.link_file_structure(
                content_types=self.content_types_field.types,
                file_types=self.file_types_field.types,
                serializer=self.serializer_field.map(lambda subcomponent: subcomponent.final),
                structure=self.structure_field.map(lambda subcomponent: subcomponent.final),
            )
