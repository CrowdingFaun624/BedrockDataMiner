from typing import Sequence

from Component.ComponentTyping import FileStructureTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field
from Component.Serializer.SerializerComponent import SERIALIZER_PATTERN
from Component.Structure.WithinStructureComponent import WithinStructureComponent
from Structure.StructureTypes.FileStructure import FileStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class FileStructureComponent(WithinStructureComponent[FileStructure]):

    __slots__ = (
        "serializer_field",
    )

    class_name = "File"
    structure_type = FileStructure
    type_verifier = WithinStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("serializer", True, (str, dict, type(None))),
    ))

    def initialize_fields(self, data: FileStructureTypedDict) -> Sequence[Field]:
        fields = list(super().initialize_fields(data))

        self.serializer_field = OptionalComponentField(data["serializer"], SERIALIZER_PATTERN, ("serializer",))

        self.variable_bools["children_has_garbage_collection"] = True
        fields.append(self.serializer_field)
        return fields

    def link_finals(self, trace: Trace) -> None:
        super().link_finals(trace)
        self.final.link_file_structure(
            serializer=self.serializer_field.map(lambda subcomponent: subcomponent.final),
        )
