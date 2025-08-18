from typing import TYPE_CHECKING

import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    from Version.Version import Version

class VersionRange():
    """
    Used for detecting if a Version is within a range of versions.
    Use None to represent not stopping, or continuing on to the end of the list.
    Checks if the version is in [start, stop).
    """

    __slots__ = (
        "start",
        "stop",
    )

    def __init__(self, start:"Version|None", stop:"Version|None") -> None:
        self.start = start if start is not None else None
        self.stop = stop if stop is not None else None
        if start is not None and stop is not None and start > stop:
            raise Exceptions.VersionRangeOrderError(self, start, stop)

    def __str__(self) -> str:
        return f"\"{str(self.start)}\"–\"{str(self.stop)}\""

    def __repr__(self) -> str:
        return f"<VersionRange \"{str(self.start)}\"–\"{str(self.stop)}\">"

    def __contains__(self, version:"Version") -> bool:
        if self.start is None and self.stop is None:
            return True
        elif self.start is None and self.stop is not None:
            return version < self.stop
        elif self.start is not None and self.stop is None:
            return version >= self.start
        elif self.start is not None and self.stop is not None:
            return version < self.stop and version >= self.start
        else:
            raise Exceptions.InvalidStateError("logic has failed us")
