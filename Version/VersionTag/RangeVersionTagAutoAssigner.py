from Version.Version import Version
from Version.VersionRange import VersionRange
from Version.VersionTag.VersionTagAutoAssigner import VersionTagAutoAssigner


class RangeVersionTagAutoAssigner(VersionTagAutoAssigner):

    __slots__ = (
        "version_range",
    )

    def link_range_version_tag_auto_assigner(self, oldest_version:Version|None, newest_version:Version|None) -> None:
        self.version_range = VersionRange(oldest_version, newest_version)

    def __call__(self, version:"Version") -> bool:
        return version in self.version_range