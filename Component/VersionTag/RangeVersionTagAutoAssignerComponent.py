from typing import Sequence

from Component.ComponentTyping import RangeVersionTagAutoAssignerTypedDict
from Component.Field.Field import Field
from Component.Version.Field.VersionRangeField import VersionRangeField
from Component.Version.VersionComponent import VersionComponent
from Component.VersionTag.VersionTagAutoAssignerComponent import (
    VersionTagAutoAssignerComponent,
)
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier


class RangeVersionTagAutoAssignerComponent(VersionTagAutoAssignerComponent):

    class_name = "RangeVersionTagAutoAssigner"
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("newest", True, (str, type(None))),
        TypedDictKeyTypeVerifier("oldest", True, (str, type(None))),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "version_range_field",
    )

    def initialize_fields(self, data: RangeVersionTagAutoAssignerTypedDict) -> Sequence[Field]:
        self.version_range_field = VersionRangeField(data["oldest"], data["newest"], ("oldest/newest",), ("oldest",), ("newest",))
        return (self.version_range_field,)

    def contains_version(self, version: "VersionComponent") -> bool:
        return version in self.version_range_field
