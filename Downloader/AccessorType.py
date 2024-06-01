import json
from typing import TYPE_CHECKING, Any, TypedDict

import Downloader.Accessor as Accessor
import Downloader.DownloadManager as DownloadManager
import Downloader.InstallManager as InstallManager
import Downloader.LocalManager as LocalManager
import Downloader.MyAccessor as MyAccessor
import Downloader.StoredManager as StoredManager
import Utilities.FileManager as FileManager
import Version.VersionFileType as VersionFileType
import Version.VersionTags as VersionTags

if TYPE_CHECKING:
    import Version.Version as Version

ACCESSORS:dict[str,type[Accessor.Accessor]] = {
    "MyAccessor": MyAccessor.MyAccessor,
}

MANAGERS:dict[str,type[InstallManager.InstallManager]] = {
    "DownloadManager": DownloadManager.DownloadManager,
    "LocalManager": LocalManager.LocalManager,
    "StoredManager": StoredManager.StoredManager,
}

class AccessorTypedDict(TypedDict):
    accessor: str
    manager: str

class AccessorType():

    def __init__(self, name:str, manager_class:type[InstallManager.InstallManager], accessor_class:type[Accessor.Accessor]) -> None:
        self.name = name
        self.manager_class = manager_class
        self.accessor_class = accessor_class

    def create_accessor(self, version:"Version.Version", file_type:VersionFileType.VersionFileType, version_tags:VersionTags.VersionTags, accessor_arguments:Any) -> Accessor.Accessor:
        self.manager_class.validate_arguments(accessor_arguments, version.name, file_type.name, self.name)
        assert version.version_folder is not None
        manager = self.manager_class(version, accessor_arguments, version.version_folder.joinpath(file_type.install_location), version_tags)
        return self.accessor_class(self.name, manager, version, accessor_arguments)

def parse_accessor_types(data:dict[str,AccessorTypedDict]) -> dict[str,AccessorType]:
    return {key: AccessorType(key, MANAGERS[accessor_data["manager"]], ACCESSORS[accessor_data["accessor"]]) for key, accessor_data in data.items()}

def import_accessor_types() -> dict[str,AccessorType]:
    with open(FileManager.ACCESSOR_TYPES_FILE, "rt") as f:
        return parse_accessor_types(json.load(f))

accessors = import_accessor_types()
