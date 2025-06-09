from typing import TYPE_CHECKING, Literal, overload

from Downloader.Accessor import Accessor
from Utilities.Exceptions import VersionFileNoAccessorsError
from Utilities.Trace import Trace
from Version.VersionFileType import VersionFileType

if TYPE_CHECKING:
    from Component.Accessor.AccessorComponent import AccessorCreator
    from Version.Version import Version

class VersionFile():

    __slots__ = (
        "_accessors",
        "accessor_creators",
        "full_name",
        "name",
        "version",
        "version_file_type",
    )

    def __init__(self, full_name:str) -> None:
        self.full_name = full_name

    def link_finals(
        self,
        version:"Version",
        version_file_type:VersionFileType,
        accessors:list["AccessorCreator"],
    ) -> None:
        self.name = version_file_type.name
        self.version = version
        self.version_file_type = version_file_type
        self.accessor_creators = accessors
        self._accessors:list[Accessor]|None = None

    @property
    def accessors(self) -> list[Accessor]:
        if self._accessors is None:
            # has potential to be None due to errors. These errors are handled
            # elsewhere
            self._accessors = [accessor for accessor_creator in self.accessor_creators if (accessor := accessor_creator.create_accessor(Trace())) is not None]
        return self._accessors

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

    def has_accessors(self) -> bool:
        "Returns True if this VersionFile has at least one Accessor."
        return len(self.accessor_creators) > 0

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
