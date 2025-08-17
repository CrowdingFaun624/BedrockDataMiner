from typing import Required, Sequence, TypedDict

from Component.Component import Component
from Downloader.AccessorType import AccessorCreator
from Utilities.Exceptions import VersionFileInvalidAccessorError
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)
from Version.VersionFile import VersionFileCreator
from Version.VersionFileType import VersionFileType


class VersionFileTypedDict(TypedDict):
    accessors: Required[Sequence[AccessorCreator]]
    version_file_type: Required[VersionFileType]

class VersionFileComponent(Component[VersionFileCreator, VersionFileTypedDict]):

    type_name = "VersionFile"
    object_type = VersionFileCreator
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("accessors", True, ListTypeVerifier(AccessorCreator, list)),
        TypedDictKeyTypeVerifier("version_file_type", True, VersionFileType),
    ))

    def link_final(self, fields: VersionFileTypedDict) -> None:
        super().link_final(fields)
        self.final.link_version_file_creator(
            accessors=fields["accessors"],
            version_file_type=fields["version_file_type"],
        )

    def post_check(self, fields: VersionFileTypedDict, trace: Trace) -> bool:
        if super().post_check(fields, trace):
            return True
        has_error:bool = False
        allowed_accessors = fields["version_file_type"].allowed_accessor_types
        for accessor_creator in fields["accessors"]:
            if accessor_creator.accessor_type not in allowed_accessors:
                trace.exception(VersionFileInvalidAccessorError(self.final, accessor_creator.name))
        return has_error
