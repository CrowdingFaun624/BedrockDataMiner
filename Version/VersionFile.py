from typing import TYPE_CHECKING, Literal, overload

import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace
import Version.VersionFileType as VersionFileType

if TYPE_CHECKING:
    import Component.Accessor.AccessorComponent as AccessorComponent
    import Version.Version as Version

class VersionFile():

    __slots__ = (
        "_accessors",
        "accessor_creators",
        "name",
        "version",
        "version_file_type",
    )

    def link_finals(
        self,
        version:"Version.Version",
        version_file_type:VersionFileType.VersionFileType,
        accessors:list["AccessorComponent.AccessorCreator"],
    ) -> None:
        self.name = version_file_type.name
        self.version = version
        self.version_file_type = version_file_type
        self.accessor_creators = accessors
        self._accessors:list[Accessor.Accessor]|None = None

    @property
    def accessors(self) -> list[Accessor.Accessor]:
        if self._accessors is None:
            # has potential to be None due to errors. These errors are handled
            # elsewhere
            self._accessors = [accessor for accessor_creator in self.accessor_creators if (accessor := accessor_creator.create_accessor(Trace.Trace())) is not None]
        return self._accessors

    def __repr__(self) -> str:
        return f"<VersionFile {self.name} of {self.version}>"

    def has_accessors(self) -> bool:
        "Returns True if this VersionFile has at least one Accessor."
        return len(self.accessor_creators) > 0

    @overload
    def get_accessor[a: Accessor.Accessor](self, required_type:type[a], none_okay:Literal[True]) -> a|None: ...
    @overload
    def get_accessor[a: Accessor.Accessor](self, required_type:type[a], none_okay:Literal[False]) -> a: ...
    @overload
    def get_accessor[a: Accessor.Accessor](self, required_type:type[a]) -> a: ...
    def get_accessor[a: Accessor.Accessor](self, required_type:type[a]=Accessor.Accessor, none_okay:bool=False) -> a|None:
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
                raise Exceptions.VersionFileNoAccessorsError(self)
