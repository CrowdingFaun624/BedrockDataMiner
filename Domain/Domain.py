import json
from collections import Counter
from itertools import chain
from pathlib import Path
from typing import Callable, Mapping, NotRequired, Sequence, TypedDict

import Utilities.CustomJson as CustomJson
import Utilities.FileManager as FileManager
from Component.Component import Component
from Component.ComponentFunctions import BUILT_INS
from Component.Group import Group
from Component.Importer import parse_all_groups
from Component.Importer import print_exceptions as importer_print_exceptions
from Component.ImporterFinalize import finalize_all as importer_finalize_all
from Component.ScriptImporter import ScriptSetSet, import_scripted_objects
from Component.ScriptReferenceable import ScriptReferenceable
from Component.Types import TypeStuff, primary_type_stuff
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Domain.LibFiles import LibFiles
from Serializer.Serializer import Serializer
from Structure.StructureTag import StructureTag
from Tablifier.Tablifier import Tablifier
from Utilities.DataFile import DataFile
from Utilities.Log import Log
from Utilities.MemoryUsage import memory_usage
from Utilities.Scripts import Scripts
from Utilities.Trace import Trace
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

def get_object_dictionary[T](
    groups:list[Group],
    object_type:type[T],
    primary_name_func:Callable[["Component[T]", Group],str]=lambda component, group: component.name,
    secondary_name_func:Callable[["Component[T]", Group],str]=lambda component, group: f"{group.name}/{component.name}",
) -> Mapping[str,T]:
    final_names:dict[tuple[str,str],T] = {}
    primary_names:Counter[str] = Counter()
    for group in groups:
        for component in group.components.values():
            if isinstance(component.final, object_type):
                primary_name, secondary_name = primary_name_func(component, group), secondary_name_func(component, group)
                final_names[primary_name, secondary_name] = component.final
                primary_names[primary_name] += 1
    return {(secondary_name if primary_names[primary_name] > 1 else primary_name): object for (primary_name, secondary_name), object in final_names.items()}

class Domain():

    __slots__ = (
        "component_log_file",
        "dataminer_collections",
        "logs",
        "serializers",
        "structure_tags",
        "tablifiers",
        "version_tags",
        "versions",
        "name",
        "assets_directory",
        "data_directory",
        "lib_directory",
        "log_directory",
        "scripts_directory",
        "domain_file",
        "versions_directory",
        "comparisons_directory",
        "data_files",
        "json_decoder",
        "json_encoder",
        "scripts",
        "script_set",
        "script_set_set",
        "lib_files",
        "type_stuff",
        "is_library",
        "aliases",
        "dependencies_str",
        "dependencies",
        "script_referenceable",
        "comparison_file_counts",
        "is_imported",
        "is_imported_scripts",
        "active_file_hashes",
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
        self.is_library:bool
        self.aliases:Sequence[str]
        self.dependencies_str:Sequence[str]
        self.dependencies:list[Domain]
        self.read_manifest()

        self.dataminer_collections:Mapping[str,"AbstractDataminerCollection"]
        self.logs:Mapping[str,"Log"]
        self.serializers:Mapping[str,"Serializer"]
        self.structure_tags:Mapping[str,"StructureTag"]
        self.tablifiers:Mapping[str,"Tablifier"]
        self.version_tags:Mapping[str,"VersionTag"]
        self.versions:Mapping[str,"Version"]

        self.data_files = self._get_data_files()
        '''
        dictionary of files in the `./_assets/data` directory without the final suffix.
        '''
        self.json_decoder:             type[json.JSONDecoder]
        self.json_encoder:             type[json.JSONEncoder]
        self.scripts:                  Scripts

        self.lib_files = LibFiles(self)
        self.type_stuff = TypeStuff(self)
        self.type_stuff.extend(primary_type_stuff)
        self.script_referenceable:ScriptReferenceable = ScriptReferenceable(self)
        self.active_file_hashes:set[int] = set()

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
        self.is_library = file.get("is_library", False)
        self.aliases = file.get("aliases", ())
        self.dependencies_str = file.get("dependencies", ())

    def link_domains(self, domains:dict[str,"Domain"]) -> None:
        self.dependencies = [domains[domain_name] for domain_name in self.dependencies_str]
        # link type stuff
        for dependency in self.dependencies:
            self.type_stuff.link(dependency.type_stuff)

    def import_components(self) -> None:
        if self.is_imported:
            return
        all_domains = self.get_cascading_dependencies(set())
        for domain in all_domains:
            domain.import_scripts()
        all_groups = parse_all_groups(all_domains)
        trace = Trace()
        for domain in all_domains:
            with trace.enter(domain, domain.name, ...):
                domain.set_values(all_groups[domain])
        importer_print_exceptions(self, trace)
        importer_finalize_all(all_groups, self, importer_print_exceptions)
        self.is_imported = True
        memory_usage.add_domain(self)

    def import_scripts(self) -> None:
        # this Domain may already have its Scripts set by another Domain.
        if self.is_imported_scripts:
            return
        self.scripts = Scripts(self)
        self.scripts.import_modules()
        self.json_decoder = CustomJson.get_special_decoder(self)
        self.json_encoder = CustomJson.get_special_encoder(self)
        self.script_set = import_scripted_objects(self, BUILT_INS)
        self.script_set_set = ScriptSetSet(self)
        self.is_imported_scripts = True

    def set_values(self, groups:list[Group]) -> None:
        self.dataminer_collections = get_object_dictionary(groups, AbstractDataminerCollection)
        self.logs = get_object_dictionary(groups, Log)
        self.serializers = get_object_dictionary(groups, Serializer)
        self.structure_tags = get_object_dictionary(groups, StructureTag)
        self.tablifiers = get_object_dictionary(groups, Tablifier)
        self.version_tags = get_object_dictionary(groups, VersionTag)
        self.versions = get_object_dictionary(groups, Version)

    def _get_data_files(self) -> dict[str,DataFile]:
        if self.data_directory.exists():
            return {path.stem: DataFile(path) for path in self.data_directory.iterdir()}
        else:
            return {}

    def get_comparison_file_path(self, name:str, number:int) -> Path:
        comparison_subdirectory = self.comparisons_directory.joinpath(name)
        comparison_subdirectory.mkdir(exist_ok=True)
        return comparison_subdirectory.joinpath(f"report_{str(number).zfill(4)}.txt")

    def close(self) -> None:
        for version in self.versions.values():
            version.close_accessors()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def __hash__(self) -> int:
        return hash(self.name)
