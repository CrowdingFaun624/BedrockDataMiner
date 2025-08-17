from typing import Required

from Component.VersionTag.VersionTagAutoAssignerComponent import (
    VersionTagAutoAssignerComponent,
    VersionTagAutoAssignerTypedDict,
)
from Utilities.TypeVerifier import TypedDictKeyTypeVerifier, TypedDictTypeVerifier
from Version.Version import Version
from Version.VersionTag.RangeVersionTagAutoAssigner import RangeVersionTagAutoAssigner


class RangeVersionTagAutoAssignerTypedDict(VersionTagAutoAssignerTypedDict):
    newest: Required[Version | None]
    oldest: Required[Version | None]

class RangeVersionTagAutoAssignerComponent(VersionTagAutoAssignerComponent[RangeVersionTagAutoAssigner, RangeVersionTagAutoAssignerTypedDict]):

    type_name = "RangeVersionTagAutoAssigner"
    object_type = RangeVersionTagAutoAssigner
    abstract = False

    type_verifier = VersionTagAutoAssignerComponent.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("newest", True, (Version, type(None))),
        TypedDictKeyTypeVerifier("oldest", True, (Version, type(None))),
    ))

    def link_final(self, fields: RangeVersionTagAutoAssignerTypedDict) -> None:
        super().link_final(fields)
        self.final.link_range_version_tag_auto_assigner(
            oldest_version=fields["oldest"],
            newest_version=fields["newest"],
        )
