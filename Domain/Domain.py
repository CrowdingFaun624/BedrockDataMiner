import json
from itertools import chain
from pathlib import Path
from typing import Mapping, NotRequired, Sequence, TypedDict

import Component.Scripts as Scripts
import Utilities.CustomJson as CustomJson
import Utilities.FileManager as FileManager
from Component.Group import GroupDirectory, ScriptFile
from Component.Importer import import_all
from Component.Types import TypeStuff, primary_type_stuff
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Domain.LibFiles import LibFiles
from Serializer.Serializer import Serializer
from Structure.StructureTag import StructureTag
from Tablifier.Tablifier import Tablifier
from Utilities.DataFile import DataFile
from Utilities.Log import Log
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)
from Version.Version import Version
from Version.VersionTag.VersionTag import VersionTag

pass # if these aren't imported here, they will never be imported and won't be added to the built-in objects
import Component.BuiltInFunctions as _
import Dataminer.BuiltIns.AllFilesDataminer as _
import Dataminer.BuiltIns.GrabMultipleFilesDataminer as _
import Dataminer.BuiltIns.GrabReFilesDataminer as _
import Dataminer.BuiltIns.GrabSingleFileDataminer as _
import Dataminer.BuiltIns.SingleFileDataminer as _
import Dataminer.BuiltIns.TagFunctionDataminer as _
import Dataminer.BuiltIns.TagSearcherDataminer as _
import Downloader.AccessorType as _
import Downloader.DownloadAccessor as _
import Downloader.DummyAccessor as _
import Downloader.SingleDirectoryFileAccessor as _
import Downloader.StoredAccessor as _
import Downloader.ZipAccessor as _
import Serializer.CustomJsonSerializer as _
import Serializer.DummySerializer as _
import Serializer.JsonSerializer as _
import Serializer.LinesSerializer as _
import Serializer.RepairableJsonSerializer as _
import Serializer.TextSerializer as _
import Structure.Delegate.DefaultBaseDelegate as _
import Structure.Delegate.DefaultDelegate as _
import Structure.Delegate.Delegate as _
import Structure.Delegate.LongStringDelegate as _
import Structure.Delegate.PrimitiveDelegate as _
import Version.VersionFileType as _
import Version.VersionProvider.LatestVersionProvider as _


class DomainManifestTypedDict(TypedDict):
    aliases: NotRequired[list[str]]
    dependencies: NotRequired[list[str]]
    is_library: NotRequired[bool]

class Domain():

    __slots__ = (
        "active_file_hashes",
        "aliases",
        "assets_directory",
        "comparison_file_counts",
        "comparisons_directory",
        "component_log_file",
        "data_directory",
        "data_files",
        "dataminer_collections",
        "dependencies",
        "dependencies_str",
        "domain_file",
        "file_tree",
        "is_imported",
        "is_imported_scripts",
        "is_library",
        "json_decoder",
        "json_encoder",
        "lib_directory",
        "lib_files",
        "log_directory",
        "logs",
        "name",
        "scripts",
        "scripts_directory",
        "serializers",
        "structure_tags",
        "tablifiers",
        "type_stuff",
        "version_tags",
        "versions",
        "versions_directory",
    )

    def __init__(self, name:str) -> None:
        self.name = name
        self.assets_directory           = FileManager.DOMAINS_DIRECTORY.joinpath(name)
        self.component_log_file         = self.assets_directory.joinpath("component_log.txt")
        self.data_directory             = self.assets_directory.joinpath("data")
        self.lib_directory              = self.assets_directory.joinpath("lib")
        self.log_directory              = self.assets_directory.joinpath("log")
        self.scripts_directory          = self.assets_directory.joinpath("scripts")
        self.domain_file                = self.assets_directory.joinpath("domain.json")
        self.versions_directory         = FileManager.VERSIONS_DIRECTORY.joinpath(name)
        self.comparisons_directory      = FileManager.COMPARISONS_DIRECTORY.joinpath(name)
        self.comparison_file_counts:dict[str, int] = {}

        self.is_imported:bool = False
        self.is_imported_scripts:bool = False
        self.type_stuff = TypeStuff(self)
        self.type_stuff.extend(primary_type_stuff)

    def get_cascading_dependencies(self, memo:set["Domain"]) -> Sequence["Domain"]:
        if self not in memo:
            output:list[Domain] = list(chain.from_iterable(dependency.get_cascading_dependencies(memo) for dependency in self.dependencies))
            memo.add(self)
            output.append(self)
            return output
        else:
            return ()

    def read_manifest(self) -> None:
        with open(self.domain_file, "rt") as f:
            file:DomainManifestTypedDict = json.load(f)
        TypedDictTypeVerifier(
            TypedDictKeyTypeVerifier("aliases", False, ListTypeVerifier(str, list)),
            TypedDictKeyTypeVerifier("is_library", False, bool),
            TypedDictKeyTypeVerifier("dependencies", False, ListTypeVerifier(str, list)),
        ).verify_throw(file, (self,))
        self.is_library:bool = file.get("is_library", False)
        self.aliases:Sequence[str] = file.get("aliases", ())
        self.dependencies_str:Sequence[str] = file.get("dependencies", ())

    def link_domains(self, domains:dict[str,"Domain"]) -> None:
        self.dependencies:Sequence[Domain] = [domains[domain_name] for domain_name in self.dependencies_str]
        # link type stuff
        for dependency in self.dependencies:
            self.type_stuff.link(dependency.type_stuff)

    def import_components(self) -> bool:
        if self.is_imported:
            return False
        result = import_all(self)
        self.is_imported = not result
        return result

    def add_file_tree(self, file_tree:GroupDirectory) -> None:
        # file_tree is used by UserScript.__init__
        self.file_tree:GroupDirectory = file_tree

    def get_script_file(self, file_name:str) -> ScriptFile:
        """
        May be called while the `file_tree` attribute exists.

        :param file_name: The file name of the Script's file, with forward slashes, relative to the Domain's directory, and without the ".py" suffix.
        """
        current_group_object = self.file_tree
        for item in file_name.split("/"):
            assert isinstance(current_group_object, GroupDirectory)
            current_group_object = current_group_object.children[item]
        assert isinstance(current_group_object, ScriptFile)
        return current_group_object

    def remove_file_tree(self) -> None:
        # remove the attribute so it may be garbage collected after importing is done
        del self.file_tree

    def import_scripts(self) -> None:
        # this Domain may already have its Scripts set by another Domain.
        if self.is_imported_scripts:
            return
        self.is_imported_scripts = True
        self.scripts = Scripts.scripts
        self.json_decoder:type[json.JSONDecoder] = CustomJson.get_special_decoder(self)
        self.json_encoder:type[json.JSONEncoder] = CustomJson.get_special_encoder(self)
        self.lib_files = LibFiles(self)
        self.active_file_hashes:set[int] = set()

    def set_values(
        self,
        dataminer_collections:Mapping[str,"AbstractDataminerCollection"],
        logs:Mapping[str,"Log"],
        serializers:Mapping[str,"Serializer"],
        structure_tags:Mapping[str,"StructureTag"],
        tablifiers:Mapping[str,"Tablifier"],
        version_tags:Mapping[str,"VersionTag"],
        versions:Mapping[str,"Version"],
    ) -> None:
        if self.is_imported:
            return # may be triggered by a Domain using this one as a library being imported
        self.dataminer_collections = dataminer_collections
        self.logs = logs
        self.serializers = serializers
        self.structure_tags = structure_tags
        self.tablifiers = tablifiers
        self.version_tags = version_tags
        self.versions = versions

    def import_data_files(self) -> None:
        self.data_files:Mapping[str,DataFile]
        """
        dictionary of files in the `./_assets/data` directory without the final suffix.
        """
        if not self.data_directory.exists():
            self.data_files = {}
            return
        self.data_files = {
            (path_name := path.relative_to(self.data_directory).as_posix().removesuffix(path.suffix)): DataFile(path, path_name)
            for path in self.data_directory.rglob("*")
        }

    def get_comparison_file_path(self, name:str, number:int) -> Path:
        comparison_subdirectory = self.comparisons_directory.joinpath(name)
        comparison_subdirectory.mkdir(exist_ok=True)
        return comparison_subdirectory.joinpath(f"report_{str(number).zfill(4)}.txt")

    def close(self) -> None:
        if self.is_imported:
            for version in self.versions.values():
                version.close_accessors()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def __hash__(self) -> int:
        return hash(self.name)
