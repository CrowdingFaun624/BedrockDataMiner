import Utilities.Version as Version

class VersionRange():
    '''Used for detecting if a Version is within a range of versions.
    Use "-" to represent not stopping, or continuing on to the end of the list.
    By default, checks if the version is in [start, stop). If start and stop are the same, it checks for equality.'''

    def __init__(self, start:Version.Version, stop:Version.Version) -> None:
        if isinstance(start, Version.Version) and isinstance(stop, Version.Version) and start > stop:
            raise ValueError("Start Version (\"%s\")in `VersionRange` occurs after stop Version (\"%s\")!" % (start.name, stop.name))
        self.start = start if start != "-" else None
        self.stop = stop if stop != "-" else None
        self.equals = self.start == self.stop and self.start is not None

    def __repr__(self) -> str:
        return "<VersionRange \"%s\"–\"%s\">" % (str(self.start), str(self.stop))

    def __contains__(self, version:Version.Version) -> bool:
        if not isinstance(version, Version.Version):
            raise TypeError("Attempting to check for non-Version object in VersionRange!")
        if self.equals:
            return version == self.start
        match (self.start is None, self.stop is None):
            case (True, True):
                return True
            case (True, False):
                return version < self.stop
            case (False, True):
                return version >= self.start
            case (False, False):
                return version < self.stop and version >= self.start
            case _:
                raise RuntimeError("Logic has failed us")
