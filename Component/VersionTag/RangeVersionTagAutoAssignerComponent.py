from typing import Sequence

from Component.ComponentTyping import RangeVersionTagAutoAssignerTypedDict
from Component.Field.ComponentField import OptionalComponentField
from Component.Field.Field import Field, InlinePermissions
from Component.Version.VersionComponent import VERSION_PATTERN
from Component.VersionTag.VersionTagAutoAssignerComponent import (
    VersionTagAutoAssignerComponent,
)
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier
from Version.VersionTag.RangeVersionTagAutoAssigner import RangeVersionTagAutoAssigner


class RangeVersionTagAutoAssignerComponent(VersionTagAutoAssignerComponent[RangeVersionTagAutoAssigner]):

    class_name = "RangeVersionTagAutoAssigner"
    type_verifier = TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("newest", True, (str, type(None))),
        TypedDictKeyTypeVerifier("oldest", True, (str, type(None))),
        TypedDictKeyTypeVerifier("type", False, str),
    )

    __slots__ = (
        "newest_field",
        "oldest_field",
    )

    def initialize_fields(self, data: RangeVersionTagAutoAssignerTypedDict) -> Sequence[Field]:
        self.oldest_field = OptionalComponentField(data["oldest"], VERSION_PATTERN, ("oldest",), allow_inline=InlinePermissions.reference)
        self.newest_field = OptionalComponentField(data["newest"], VERSION_PATTERN, ("newest",), allow_inline=InlinePermissions.reference)
        return (self.oldest_field, self.newest_field)

    def create_final(self, trace: Trace) -> RangeVersionTagAutoAssigner:
        return RangeVersionTagAutoAssigner(
            full_name=self.full_name,
        )

    def link_finals(self, trace: Trace) -> None:
        self.final.link(
            oldest_version=self.oldest_field.map(lambda component: component.final),
            newest_version=self.newest_field.map(lambda component: component.final),
        )
