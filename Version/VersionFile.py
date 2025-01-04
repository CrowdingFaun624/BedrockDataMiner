from typing import TYPE_CHECKING, Literal, overload

import Downloader.Accessor as Accessor
import Utilities.Exceptions as Exceptions
import Version.VersionFileType as VersionFileType

if TYPE_CHECKING:
    import Component.Accessor.AccessorComponent as AccessorComponent
    import Version.Version as Version

class VersionFile():

    def __init__(self) -> None:
        self.name:str|None = None
        self.version:"Version.Version|None" = None
        self.version_file_type:VersionFileType.VersionFileType|None = None
        self.accessors:list["AccessorComponent.AccessorCreator"]|None = None

    def link_finals(
        self,
        version:"Version.Version",
        version_file_type:VersionFileType.VersionFileType,
        accessors:list["AccessorComponent.AccessorCreator"],
    ) -> None:
        self.name = version_file_type.name
        self.version = version
        self.version_file_type = version_file_type
        self.accessors = accessors

    def get_name(self) -> str:
        if self.name is None:
            raise Exceptions.AttributeNoneError("name", self)
        return self.name

    def get_version(self) -> "Version.Version":
        if self.version is None:
            raise Exceptions.AttributeNoneError("version", self)
        return self.version

    def get_version_file_type(self) -> VersionFileType.VersionFileType:
        if self.version_file_type is None:
            raise Exceptions.AttributeNoneError("version_file_type", self)
        return self.version_file_type

    def get_accessors(self) -> list[Accessor.Accessor]:
        if self.accessors is None:
            raise Exceptions.AttributeNoneError("accessors", self)
        # has potential to be None due to errors. These errors are handled
        # elsewhere
        return [accessor for accessor_creator in self.accessors if (accessor := accessor_creator.create_accessor()[0]) is not None]

    def __repr__(self) -> str:
        return f"<VersionFile {self.get_version_file_type().name} of {self.get_version().name}>"

    def has_accessors(self) -> bool:
        "Returns True if this VersionFile has at least one Accessor."
        if self.accessors is None:
            raise Exceptions.AttributeNoneError("accessors", self)
        return len(self.accessors) > 0

    @overload
    def get_accessor[a: Accessor.Accessor](self, none_okay:Literal[True], *, required_type:type[a]=Accessor.Accessor) -> a|None: ...
    @overload
    def get_accessor[a: Accessor.Accessor](self, none_okay:Literal[False], *, required_type:type[a]=Accessor.Accessor) -> a: ...
    @overload
    def get_accessor[a: Accessor.Accessor](self, *, required_type:type[a]=Accessor.Accessor) -> a: ...
    def get_accessor[a: Accessor.Accessor](self, none_okay:bool=False, *, required_type:type[a]=Accessor.Accessor) -> a|None:
        '''
        Returns the first Accessor of this VersionFile that meets the requirements.
        :required_type: Type of the Accessor.
        '''
        for accessor in self.get_accessors():
            if not isinstance(accessor, required_type):
                continue
            return accessor
        else:
            if none_okay:
                return None
            else:
                raise Exceptions.VersionFileNoAccessorsError(self)
