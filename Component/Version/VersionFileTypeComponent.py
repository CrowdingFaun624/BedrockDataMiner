from typing import NotRequired, Required, Sequence, TypedDict

from Component.Component import Component
from Downloader.AccessorType import AccessorType
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)
from Version.VersionFileType import VersionFileType


class VersionFileTypeTypedDict(TypedDict):
    allowed_accessor_types: Required[AccessorType | Sequence[AccessorType]]
    dependencies: NotRequired[VersionFileType | Sequence[VersionFileType]]
    available_when_unreleased: Required[bool]
    must_exist: Required[bool]

def convert_accessor_types_to_sequence(sequence: AccessorType | Sequence[AccessorType]) -> Sequence[AccessorType]:
    return [sequence] if isinstance(sequence, AccessorType) else sequence

def convert_version_file_types_to_sequence(sequence: VersionFileType | Sequence[VersionFileType]) -> Sequence[VersionFileType]:
    return [sequence] if isinstance(sequence, VersionFileType) else sequence

class VersionFileTypeComponent(Component[VersionFileType, VersionFileTypeTypedDict]):

    type_name = "VersionFileType"
    object_type = VersionFileType
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("allowed_accessor_types", True, UnionTypeVerifier(AccessorType, ListTypeVerifier(AccessorType, list))),
        TypedDictKeyTypeVerifier("dependencies", False, UnionTypeVerifier(VersionFileType, ListTypeVerifier(VersionFileType, list))),
        TypedDictKeyTypeVerifier("available_when_unreleased", True, bool),
        TypedDictKeyTypeVerifier("must_exist", True, bool),
    ))

    def link_final(self, fields: VersionFileTypeTypedDict) -> None:
        super().link_final(fields)
        self.final.link_version_file_type(
            allowed_accessor_types=convert_accessor_types_to_sequence(fields["allowed_accessor_types"]),
            available_when_unreleased=fields["available_when_unreleased"],
            dependencies=convert_version_file_types_to_sequence(fields.get("dependencies", ())),
            must_exist=fields["must_exist"],
        )
