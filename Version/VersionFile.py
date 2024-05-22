from typing import TYPE_CHECKING, Any

from pathlib2 import Path

import Downloader.DownloadManager as DownloadManager
import Downloader.InstallManager as InstallManager
import Downloader.LocalManager as LocalManager
import Downloader.StoredManager as StoredManager
import Version.VersionFileType as VersionFileType
import Version.VersionTags as VersionTags

if TYPE_CHECKING:
    import Version.Version as Version

ACCESSORS:dict[str,type[InstallManager.InstallManager]] = {
    "download": DownloadManager.DownloadManager,
    "local": LocalManager.LocalManager,
    "stored": StoredManager.StoredManager
}

class VersionFile():

    def __init__(self, version:"Version.Version", file_type:VersionFileType.VersionFileType, accessors:dict[str,dict[str,Any]], version_tags:VersionTags.VersionTags) -> None:
        self.version = version
        self.file_type = file_type

        for accessor in accessors:
            if accessor not in self.file_type.allowed_accessors:
                raise ValueError("File Type %s for version %s does not recognize accessor \"%s\"!" % (self.file_type.name, self.version.name, accessor))

        # sort this VersionFile's accessors in the same way as its FileType
        assert version.version_folder is not None
        self.accessors:dict[str,InstallManager.InstallManager] = {}
        for allowed_accessor in self.file_type.allowed_accessors:
            if allowed_accessor in accessors:
                accessor_class = ACCESSORS[allowed_accessor]
                accessor_class.validate_arguments(accessors[allowed_accessor], version.name, file_type.name, allowed_accessor)
                self.accessors[allowed_accessor] = accessor_class(self.version, accessors[allowed_accessor], Path(version.version_folder.joinpath(self.file_type.install_location)), version_tags)
                print(version.version_folder, self.accessors[allowed_accessor].location)

    def __repr__(self) -> str:
        return "<VersionFile %s of %s>" % (self.file_type.name, self.version.name)

    def get_accessor(self) -> InstallManager.InstallManager:
        for accessor_name, accessor in self.accessors.items():
            if True: return accessor
        else:
            raise RuntimeError("Cannot get accessor of %s!" % (self))
