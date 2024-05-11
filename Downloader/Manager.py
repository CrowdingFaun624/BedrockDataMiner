import requests
import zipfile

from typing import Any, Callable, IO, TypedDict, TYPE_CHECKING
from typing_extensions import NotRequired, Required

from pathlib2 import Path

import Structure.Importer.ComponentTyping as ComponentTyping
import Structure.Importer.Importer as ComponentImporter
import Structure.Importer.ImporterConfig as ImporterConfig
import Structure.StructureFunctions as StructureFunctions
import Structure.Normalizer as Normalizer
import Utilities.Scripts as Scripts

if TYPE_CHECKING:
    import Version.Version as Version

class ManagerTypedDict(TypedDict):
    script_location: Required[str]
    argument_structure: Required[dict[str,ComponentTyping.ComponentTypedDicts]]

importer_config = ImporterConfig.ImporterConfig(allow_normalizer_dependencies=False)

class VersionIO():

    def __init__(self, version:"Version.Version") -> None:
        assert version.version_folder is not None
        self.files_directory = (version.version_folder).joinpath("files")

    def open(self, path:str, mode:str) -> IO:
        result_path = Path(self.files_directory.join(path))
        if self.files_directory not in result_path.parents:
            raise ValueError("Invalid file path \"%s\" located at \"%s\"!" % (path, result_path))
        return open(result_path, mode)

class ManagerPermissions():

    def __init__(self) -> None:
        pass

class ManagerFunctionsTableTypedDict(TypedDict):
    install: Required[Callable[[VersionIO],None]]
    is_installed: Required[Callable[[VersionIO],bool]]
    open: Required[Callable[[VersionIO],dict[str,Callable]]]
    uninstall: Required[Callable[[VersionIO],None]]

class Manager():

    def __init__(self, name:str, data:ManagerTypedDict) -> None:
        self.name = name
        self.script = Scripts.scripts[data["script_location"]]
        self.functions:ManagerFunctionsTableTypedDict = self.script()
        self.structure = ComponentImporter.parse_structure_file(self.name, data["argument_structure"], StructureFunctions.functions, importer_config)

    def get_permissions(self, version:"Version.Version") -> ManagerPermissions:
        pass

    def scan_manager_arguments(self, version_name:str, file_name:str, data:Any) -> Any:
        '''Normalizes the manager arguments, returns the normalized data. Raises an exception if the arguments of this manager are invalid.'''
        normalized_data = self.structure.normalize(data, Normalizer.NullNormalizerDependencies())
        self.structure.check_types(normalized_data)
        return normalized_data

    def install(self, io:VersionIO) -> None:
        return self.functions["install"](io)

    def is_installed(self, io:VersionIO) -> bool:
        return self.functions["is_installed"](io)

    def open(self, io:VersionIO) -> dict[str,Callable]:
        return self.functions["open"](io)

    def uninstall(self, io:VersionIO) -> None:
        return self.functions["uninstall"](io)
