from typing import TYPE_CHECKING, Any

from pathlib2 import Path

import Downloader.Accessor as Accessor
import Downloader.MyAccessor as MyAccessor
import Downloader.DownloadManager as DownloadManager
import Downloader.InstallManager as InstallManager
import Downloader.LocalManager as LocalManager
import Downloader.StoredManager as StoredManager
import Version.VersionFileType as VersionFileType
import Version.VersionTags as VersionTags

if TYPE_CHECKING:
    import Version.Version as Version

MANAGERS:dict[str,type[InstallManager.InstallManager]] = {
    "download": DownloadManager.DownloadManager,
    "local": LocalManager.LocalManager,
    "stored": StoredManager.StoredManager
}

class VersionFile():

    def __init__(self, version:"Version.Version", file_type:VersionFileType.VersionFileType, accessors:dict[str,Any], version_tags:VersionTags.VersionTags) -> None:
        self.version = version
        self.file_type = file_type

        for accessor in accessors:
            if accessor not in self.file_type.allowed_accessors:
                raise ValueError("File Type %s for version %s does not recognize accessor \"%s\"!" % (self.file_type.name, self.version.name, accessor))

        # sort this VersionFile's accessors in the same way as its FileType
        assert version.version_folder is not None
        self.accessors:dict[str,Accessor.Accessor] = {}
        for allowed_accessor in self.file_type.allowed_accessors:
            if allowed_accessor in accessors:
                manager_class = MANAGERS[allowed_accessor]
                manager_class.validate_arguments(accessors[allowed_accessor], version.name, file_type.name, allowed_accessor)
                manager = manager_class(self.version, accessors[allowed_accessor], Path(version.version_folder.joinpath(self.file_type.install_location)), version_tags)
                self.accessors[allowed_accessor] = MyAccessor.MyAccessor(allowed_accessor, manager, version, accessors[allowed_accessor])

    def __repr__(self) -> str:
        return "<VersionFile %s of %s>" % (self.file_type.name, self.version.name)

    def get_accessor(self) -> Accessor.Accessor:
        for accessor_name, accessor in self.accessors.items():
            if True: return accessor
        else:
            raise RuntimeError("Cannot get accessor of %s!" % (self))
