from typing import NotRequired, Sequence, TypedDict

from Component.Component import Component
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)
from Version.VersionTag.LatestSlot import LatestSlot
from Version.VersionTag.VersionTag import VersionTag
from Version.VersionTag.VersionTagAutoAssigner import VersionTagAutoAssigner


class VersionTagTypedDict(TypedDict):
    auto_assign: NotRequired[VersionTagAutoAssigner | Sequence[VersionTagAutoAssigner]]
    development_name: NotRequired[str]
    is_development_tag: NotRequired[bool]
    is_fork_tag: NotRequired[bool]
    is_major_tag: NotRequired[bool]
    is_order_tag: NotRequired[bool]
    is_unreleased_tag: NotRequired[bool]
    latest_slot: NotRequired[LatestSlot | None]

def convert_version_tag_auto_assigners_to_sequence(sequence: VersionTagAutoAssigner | Sequence[VersionTagAutoAssigner]) -> Sequence[VersionTagAutoAssigner]:
    return (sequence,) if isinstance(sequence, VersionTagAutoAssigner) else sequence

class VersionTagComponent(Component[VersionTag, VersionTagTypedDict]):

    type_name = "VersionTag"
    object_type = VersionTag
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("auto_assign", False, UnionTypeVerifier(VersionTagAutoAssigner, ListTypeVerifier(VersionTagAutoAssigner, list))),
        TypedDictKeyTypeVerifier("development_name", False, str),
        TypedDictKeyTypeVerifier("is_development_tag", False, bool),
        TypedDictKeyTypeVerifier("is_fork_tag", False, bool),
        TypedDictKeyTypeVerifier("is_major_tag", False, bool),
        TypedDictKeyTypeVerifier("is_order_tag", False, bool),
        TypedDictKeyTypeVerifier("is_unreleased_tag", False, bool),
        TypedDictKeyTypeVerifier("latest_slot", False, (LatestSlot, type(None))),
    ))

    def link_final(self, fields: VersionTagTypedDict) -> None:
        super().link_final(fields)
        self.final.link_version_tag(
            auto_assign=convert_version_tag_auto_assigners_to_sequence(fields.get("auto_assign", ())),
            development_name=fields.get("development_name", "dev"),
            is_development_tag=fields.get("is_development_tag", False),
            is_fork_tag=fields.get("is_fork_tag", False),
            is_major_tag=fields.get("is_major_tag", False),
            is_order_tag=fields.get("is_order_tag", False),
            is_unreleased_tag=fields.get("is_unreleased_tag", False),
            latest_slot=fields.get("latest_slot", None)
        )
