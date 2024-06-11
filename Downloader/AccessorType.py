import json
from typing import TYPE_CHECKING, Any, TypedDict

import Downloader.Accessor as Accessor
import Downloader.DownloadManager as DownloadManager
import Downloader.DummyManager as DummyManager
import Downloader.LocalManager as LocalManager
import Downloader.Manager as Manager
import Downloader.StoredManager as StoredManager
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.Scripts as Scripts
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier
import Utilities.TypeVerifier.TypeVerifierImporter as TypeVerifierImporter
import Version.VersionFileType as VersionFileType
import Version.VersionTags as VersionTags

if TYPE_CHECKING:
    import Version.Version as Version

BUILT_IN_ACCESSORS:dict[str,type[Accessor.Accessor]] = {accessor_class.__name__: accessor_class for accessor_class in [
    Accessor.Accessor,
    Accessor.DummyAccessor,
    Accessor.SubDirectoryAccessor
]}

MANAGERS:dict[str,type[Manager.Manager]] = {manager_class.__name__: manager_class for manager_class in [
    DownloadManager.DownloadManager,
    DummyManager.DummyManager,
    LocalManager.LocalManager,
    StoredManager.StoredManager,
]}

class AccessorTypedDict(TypedDict):
    accessor: str
    manager: str
    parameters: TypeVerifierImporter.TypedVerifierTypedDicts

type_verifier = TypeVerifier.DictTypeVerifier(dict, str, TypeVerifier.TypedDictTypeVerifier(
    TypeVerifier.TypedDictKeyTypeVerifier("accessor", "a str", True, str),
    TypeVerifier.TypedDictKeyTypeVerifier("manager", "a str", True, str),
    TypeVerifier.TypedDictKeyTypeVerifier("parameters", "a TypeVerifier", True, dict, function=TypeVerifierImporter.type_verify_type_verifier)
), "a dict", "a str", "a dict")

class AccessorType():

    def __init__(self, name:str, manager_class:type[Manager.Manager], accessor_class:type[Accessor.Accessor], parameters:TypeVerifier.TypeVerifier) -> None:
        self.name = name
        self.manager_class = manager_class
        self.accessor_class = accessor_class
        self.parameters = parameters

    def create_accessor(self, version:"Version.Version", file_type:VersionFileType.VersionFileType, version_tags:VersionTags.VersionTags, accessor_arguments:Any) -> Accessor.Accessor:
        self.parameters.base_verify(accessor_arguments, [version.name, file_type.name, self.name])
        manager = self.manager_class(version, accessor_arguments, version.get_version_directory().joinpath(file_type.install_location), version_tags)
        return self.accessor_class(self.name, manager, version, accessor_arguments)

def parse_accessor_types(data:dict[str,AccessorTypedDict]) -> dict[str,AccessorType]:
    accessor_scripts = Scripts.scripts.get_all_in_directory("accessors/")
    accessor_types:dict[str,type[Accessor.Accessor]] = {}
    for file_name, script in accessor_scripts.items():
        class_name = file_name.removeprefix("accessors/").removesuffix(".lua").replace("/", ".")
        attributes = dict(script())
        inherit_from:str = attributes.pop("inherit", None)
        if inherit_from is None:
            raise Exceptions.AccessorTypeMissingInheritError(class_name)
        superclass = BUILT_IN_ACCESSORS.get(inherit_from, None)
        if superclass is None:
            raise Exceptions.AccessorTypeInheritUnrecognizedAccessorTypeError(class_name, inherit_from)
        accessor_types[class_name] = type(class_name, (superclass, Scripts.ScriptedObject), dict(script()))

    output:dict[str,AccessorType] = {}
    for key, accessor_data in data.items():
        accessor_type = accessor_types.get(accessor_data["accessor"], None)
        if accessor_type is None:
            raise Exceptions.UnrecognizedAccessorTypeError(accessor_data["accessor"], source_str="AccessorType \"%s\"" % (key,))
        output[key] = AccessorType(key, MANAGERS[accessor_data["manager"]], accessor_types[accessor_data["accessor"]], TypeVerifierImporter.parse_type_verifier(accessor_data["parameters"]))
    return output

def import_accessor_types() -> dict[str,AccessorType]:
    with open(FileManager.ACCESSOR_TYPES_FILE, "rt") as f:
        data = json.load(f)
        type_verifier.base_verify(data, [FileManager.ACCESSOR_TYPES_FILE.name])
        return parse_accessor_types(data)

accessors = import_accessor_types()
