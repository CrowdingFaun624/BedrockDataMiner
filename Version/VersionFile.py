from typing import TYPE_CHECKING, Any

import Downloader.Accessor as Accessor
import Downloader.AccessorType as AccessorType
import Utilities.Exceptions as Exceptions
import Version.VersionFileType as VersionFileType
import Version.VersionTags as VersionTags

if TYPE_CHECKING:
    import Version.Version as Version

class VersionFile():

    def __init__(self, version:"Version.Version", file_type:VersionFileType.VersionFileType, accessors:dict[str,Any], version_tags:VersionTags.VersionTags) -> None:
        self.version = version
        self.file_type = file_type

        for accessor in accessors:
            if accessor not in self.file_type.allowed_accessors:
                raise Exceptions.VersionFileInvalidAccessorError(self, accessor)

        # sort this VersionFile's accessors in the same way as its FileType
        self.accessors:dict[str,Accessor.Accessor] = {}
        for allowed_accessor in self.file_type.allowed_accessors:
            if allowed_accessor in accessors:
                accessor_arguments = accessors[allowed_accessor]
                self.accessors[allowed_accessor] = AccessorType.accessors[allowed_accessor].create_accessor(version, file_type, version_tags, accessor_arguments)

    def __repr__(self) -> str:
        return "<VersionFile %s of %s>" % (self.file_type.name, self.version.name)

    def get_accessor(self) -> Accessor.Accessor:
        for accessor_name, accessor in self.accessors.items():
            if True: return accessor
        else:
            raise Exceptions.VersionFileNoAccessorsError(self)
