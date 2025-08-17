from typing import AbstractSet, Any, Mapping, Required

from Component.Structure.WithinStructureComponent import (
    WithinStructureComponent,
    WithinStructureTypedDict,
)
from Serializer.Serializer import SerializerCreator
from Structure.StructureTypes.FileStructure import FileStructure
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class FileStructureTypedDict(WithinStructureTypedDict):
    serializer: Required[SerializerCreator | None]

class FileStructureComponent(WithinStructureComponent[FileStructure, FileStructureTypedDict]):

    type_name = "File"
    object_type = FileStructure
    abstract = False

    type_verifier = WithinStructureComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("serializer", True, (SerializerCreator, type(None))),
    ))

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        serializer_creator = self.fields["serializer"]
        if serializer_creator is not None:
            serializer_creator.finalize_serializer_creator()
        self.final.finalize_file_structure(
            serializer=None if serializer_creator is None else serializer_creator.serializer
        )
        return False
