from datetime import datetime
from typing import AbstractSet, Any, Mapping, Required, Sequence, TypedDict

from Component.Component import Component
from Utilities.Trace import Trace
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
    UnionTypeVerifier,
)
from Version.Version import Version
from Version.VersionFile import VersionFileCreator
from Version.VersionTag.VersionTag import VersionTag


class VersionTypedDict(TypedDict):
    files: Required[Sequence[VersionFileCreator]]
    parent: Required[Version | None]
    tags: Required[VersionTag | Sequence[VersionTag]]
    time: Required[str | None]

def convert_tags_to_sequence(sequence:VersionTag | Sequence[VersionTag]) -> Sequence[VersionTag]:
    return [sequence] if isinstance(sequence, VersionTag) else sequence

class VersionComponent(Component[Version, VersionTypedDict]):

    type_name = "Version"
    object_type = Version
    abstract = False

    type_verifier = Component.type_verifier.extend(TypedDictTypeVerifier(
        TypedDictKeyTypeVerifier("files", True, ListTypeVerifier(VersionFileCreator, list)),
        TypedDictKeyTypeVerifier("parent", True, (Version, type(None))),
        TypedDictKeyTypeVerifier("tags", True, UnionTypeVerifier(VersionTag, ListTypeVerifier(VersionTag, list))),
        TypedDictKeyTypeVerifier("time", True, (str, type(None))),
    ))

    def check(self, fields: VersionTypedDict, trace: Trace) -> bool:
        if super().check(fields, trace):
            return True
        try:
            datetime.fromisoformat(fields["time"]) if fields["time"] is not None else None
        except Exception as e:
            trace.exception(e)
            return True
        else:
            return False

    def link_final(self, fields: VersionTypedDict) -> None:
        super().link_final(fields)
        self.final.link_version(
            index=self.index,
            parent=fields["parent"],
            tags=convert_tags_to_sequence(fields["tags"]),
            time=datetime.fromisoformat(fields["time"]) if fields["time"] is not None else None,
            version_files=fields["files"],
        )

    def finalize(self, propagating_booleans: Mapping[str, bool], propagating_sets: Mapping[str, AbstractSet[Any]], trace: Trace) -> bool:
        if super().finalize(propagating_booleans, propagating_sets, trace):
            return True
        self.final.finalize_version(trace)
        return False
