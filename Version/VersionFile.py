from typing import TYPE_CHECKING, Literal, Sequence, overload

import Domain.Domain as Domain
from Component.ComponentObject import ComponentObject
from Downloader.Accessor import Accessor
from Downloader.AccessorType import AccessorCreator
from Utilities.Exceptions import VersionFileNoAccessorsError
from Utilities.Trace import Trace
from Version.VersionFileType import VersionFileType

if TYPE_CHECKING:
    from Version.Version import Version

class VersionFileCreator(ComponentObject):

    __slots__ = (
        "accessor_creators",
        "version_file_type",
    )

    def link_version_file_creator(self, accessors:Sequence[AccessorCreator], version_file_type:VersionFileType) -> None:
        self.accessor_creators = accessors
        self.version_file_type = version_file_type

    def create_version_file(self, version:"Version") -> "VersionFile":
        return VersionFile(self.full_name, version, self.domain, self.version_file_type, self.accessor_creators)

class VersionFile():

    __slots__ = (
        "_accessors",
        "accessor_creators",
        "domain",
        "full_name",
        "name",
        "version",
        "version_file_type",
    )

    def __init__(
        self,
        full_name:str,
        version:"Version",
        domain:"Domain.Domain",
        version_file_type:VersionFileType,
        accessor_creators:Sequence[AccessorCreator],
    ) -> None:
        self.full_name = full_name
        self.name = version_file_type.name
        self.domain = domain
        self.version = version
        self.version_file_type = version_file_type
        self.accessor_creators = accessor_creators
        self._accessors:Sequence[Accessor]|None = None

    @property
    def accessors(self) -> Sequence[Accessor]:
        if self._accessors is None:
            trace = Trace()
            self._accessors = [accessor for accessor_creator in self.accessor_creators if (accessor := accessor_creator.create_accessor(self.version, self.domain, self.version_file_type, trace)) is not None]
            if trace.has_exceptions:
                print("\n".join(trace.stringify()))
                raise RuntimeError()
        return self._accessors

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

    def has_accessors(self) -> bool:
        "Returns True if this VersionFile has at least one Accessor."
        return len(self.accessors) > 0

    @overload
    def get_accessor[a: Accessor](self, required_type:type[a], none_okay:Literal[True]) -> a|None: ...
    @overload
    def get_accessor[a: Accessor](self, required_type:type[a], none_okay:Literal[False]) -> a: ...
    @overload
    def get_accessor[a: Accessor](self, required_type:type[a]) -> a: ...
    def get_accessor[a: Accessor](self, required_type:type[a]=Accessor, none_okay:bool=False) -> a|None:
        '''
        Returns the first Accessor of this VersionFile that meets the requirements.
        :required_type: Type of the Accessor.
        '''
        for accessor in self.accessors:
            if not isinstance(accessor, required_type):
                continue
            return accessor
        else:
            if none_okay:
                return None
            else:
                raise VersionFileNoAccessorsError(self)
