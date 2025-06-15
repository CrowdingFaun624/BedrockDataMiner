import json
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, NotRequired, Sequence, TypedDict

import Component.ScriptImporter as ScriptImporter
import Utilities.CustomJson as CustomJson
import Utilities.FileManager as FileManager
from Component.ComponentFunctions import functions
from Component.Importer import parse_all_component_groups
from Component.ScriptImporter import ScriptSet
from Component.ScriptReferenceable import ScriptReferenceable
from Component.Types import TypeStuff, primary_type_stuff
from Dataminer.BuiltIns.AllFilesDataminer import AllFilesDataminer
from Dataminer.BuiltIns.GrabMultipleFilesDataminer import GrabMultipleFilesDataminer
from Dataminer.BuiltIns.GrabReFilesDataminer import GrabReFilesDataminer
from Dataminer.BuiltIns.GrabSingleFileDataminer import GrabSingleFileDataminer
from Dataminer.BuiltIns.SingleFileDataminer import SingleFileDataminer
from Dataminer.BuiltIns.TagSearcherDataminer import TagSearcherDataminer
from Dataminer.Dataminer import Dataminer
from Domain.LibFiles import LibFiles
from Downloader.Accessor import Accessor
from Downloader.DownloadAccessor import DownloadAccessor
from Downloader.DummyAccessor import DummyAccessor
from Downloader.SingleDirectoryFileAccessor import SingleDirectoryFileAccessor
from Downloader.StoredAccessor import StoredAccessor
from Downloader.ZipAccessor import ZipAccessor
from Serializer.CustomJsonSerializer import CustomJsonSerializer
from Serializer.DummySerializer import DummySerializer
from Serializer.JsonSerializer import JsonSerializer
from Serializer.LinesSerializer import LinesSerializer
from Serializer.RepairableJsonSerializer import RepairableJsonSerializer
from Serializer.Serializer import Serializer
from Serializer.TextSerializer import TextSerializer
from Structure.Delegate.DefaultBaseDelegate import DefaultBaseDelegate
from Structure.Delegate.DefaultDelegate import DefaultDelegate
from Structure.Delegate.Delegate import Delegate
from Structure.Delegate.LongStringDelegate import LongStringDelegate
from Structure.Delegate.PrimitiveDelegate import PrimitiveDelegate
from Utilities.DataFile import DataFile
from Utilities.MemoryUsage import memory_usage
from Utilities.Scripts import Scripts
from Utilities.TypeVerifier import (
    ListTypeVerifier,
    TypedDictKeyTypeVerifier,
    TypedDictTypeVerifier,
)
from Version.VersionProvider.LatestVersionProvider import LatestVersionProvider
from Version.VersionProvider.VersionProvider import VersionProvider

if TYPE_CHECKING:
    from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
    from Downloader.AccessorType import AccessorType
    from Serializer.Serializer import Serializer
    from Structure.StructureBase import StructureBase
    from Structure.StructureTag import StructureTag
    from Tablifier.Tablifier import Tablifier
    from Utilities.Log import Log
    from Version.Version import Version
    from Version.VersionFileType import VersionFileType
    from Version.VersionTag.VersionTag import VersionTag
    from Version.VersionTag.VersionTagOrder import VersionTagOrder

BUILT_IN_ACCESSOR_CLASSES:dict[str,type[Accessor]] = {accessor_class.__name__: accessor_class for accessor_class in [
    DownloadAccessor,
    DummyAccessor,
    SingleDirectoryFileAccessor,
    StoredAccessor,
    ZipAccessor,
]}

BUILT_IN_DATAMINER_CLASSES:dict[str,type[Dataminer]] = {dataminer_class.__name__: dataminer_class for dataminer_class in [
    Dataminer,
    AllFilesDataminer,
    GrabMultipleFilesDataminer,
    GrabReFilesDataminer,
    GrabSingleFileDataminer,
    SingleFileDataminer,
    TagSearcherDataminer,
]}

BUILT_IN_DELEGATE_CLASSES:dict[str,type[Delegate]] = {delegate_type.__name__: delegate_type for delegate_type in [
    Delegate,
    DefaultDelegate,
    DefaultBaseDelegate,
    LongStringDelegate,
    PrimitiveDelegate,
]}

BUILT_IN_SERIALIZER_CLASSES:dict[str,type[Serializer]] = {dataminer_class.__name__: dataminer_class for dataminer_class in [
    CustomJsonSerializer,
    DummySerializer,
    JsonSerializer,
    LinesSerializer,
    RepairableJsonSerializer,
    Serializer,
    TextSerializer,
]}

BUILT_IN_VERSION_PROVIDER_CLASSES:dict[str,type[VersionProvider]] = {version_provider_class.__name__: version_provider_class for version_provider_class in [
    LatestVersionProvider,
]}

class DomainManifestTypedDict(TypedDict):
    aliases: NotRequired[list[str]]
    dependencies: NotRequired[list[str]]
    is_library: NotRequired[bool]

class Domain():

    __slots__ = (
        "accessor_types",
        "component_log_file",
        "dataminer_collections",
        "latest_slots",
        "logs",
        "serializers",
        "structures",
        "structure_tags",
        "tablifiers",
        "version_file_types",
        "version_tags_order",
        "version_tags",
        "versions",
        "name",
        "assets_directory",
        "data_directory",
        "lib_directory",
        "log_directory",
        "logs_file",
        "scripts_directory",
        "structures_directory",
        "accessor_types_file",
        "dataminer_collections_file",
        "domain_file",
        "serializers_file",
        "structure_tags_file",
        "tablifiers_file",
        "version_file_types_file",
        "version_tags_directory",
        "latest_slots_file",
        "version_tags_file",
        "version_tags_order_file",
        "versions_file",
        "versions_directory",
        "comparisons_directory",
        "data_files",
        "json_decoder",
        "json_encoder",
        "scripts",
        "accessor_classes",
        "dataminer_classes",
        "delegate_classes",
        "serializer_classes",
        "version_provider_classes",
        "lib_files",
        "type_stuff",
        "is_library",
        "aliases",
        "dependencies_str",
        "dependencies",
        "callables",
        "script_referenceable",
        "comparison_file_counts",
        "is_imported",
        "active_file_hashes",
    )

    def __init__(self, name:str) -> None:
        self.name = name
        self.assets_directory           = FileManager.DOMAINS_DIRECTORY.joinpath(name)
        self.component_log_file         = self.assets_directory.joinpath("component_log.txt")
        self.data_directory             = self.assets_directory.joinpath("data")
        self.lib_directory              = self.assets_directory.joinpath("lib")
        self.log_directory              = self.assets_directory.joinpath("log")
        self.logs_file                  = self.assets_directory.joinpath("logs.json")
        self.scripts_directory          = self.assets_directory.joinpath("scripts")
        self.structures_directory       = self.assets_directory.joinpath("structures")
        self.accessor_types_file        = self.assets_directory.joinpath("accessor_types.json")
        self.dataminer_collections_file = self.assets_directory.joinpath("dataminer_collections.json")
        self.domain_file                = self.assets_directory.joinpath("domain.json")
        self.serializers_file           = self.assets_directory.joinpath("serializers.json")
        self.structure_tags_file        = self.assets_directory.joinpath("structure_tags.json")
        self.tablifiers_file            = self.assets_directory.joinpath("tablifiers.json")
        self.version_file_types_file    = self.assets_directory.joinpath("version_file_types.json")
        self.version_tags_directory     = self.assets_directory.joinpath("version_tag")
        self.latest_slots_file          = self.version_tags_directory.joinpath("latest_slots.json")
        self.version_tags_file          = self.version_tags_directory.joinpath("version_tags.json")
        self.version_tags_order_file    = self.version_tags_directory.joinpath("version_tags_order.json")
        self.versions_file              = self.assets_directory.joinpath("versions.json")
        self.versions_directory         = FileManager.VERSIONS_DIRECTORY.joinpath(name)
        self.comparisons_directory      = FileManager.COMPARISONS_DIRECTORY.joinpath(name)
        self.comparison_file_counts:dict[str, int] = {}

        self.is_imported:bool = False
        self.is_library:bool
        self.aliases:Sequence[str]
        self.dependencies_str:Sequence[str]
        self.dependencies:list[Domain]
        self.read_manifest()

        self.accessor_types:dict[str,"AccessorType"]
        self.dataminer_collections:dict[str,"AbstractDataminerCollection"]
        self.latest_slots:list[str]
        self.logs:dict[str,"Log"]
        self.serializers:dict[str,"Serializer"]
        self.structures:dict[str,"StructureBase"]
        self.structure_tags:dict[str,"StructureTag"]
        self.tablifiers:dict[str,"Tablifier"]
        self.version_file_types:dict[str,"VersionFileType"]
        self.version_tags_order:"VersionTagOrder"
        self.version_tags:dict[str,"VersionTag"]
        self.versions:dict[str,"Version"]

        self.data_files = self._get_data_files()
        '''
        dictionary of files in the `./_assets/data` directory without the final suffix.
        '''
        self.json_decoder:             type[json.JSONDecoder]
        self.json_encoder:             type[json.JSONEncoder]
        self.scripts:                  Scripts
        self.callables:                ScriptSet[Callable]
        self.accessor_classes:         ScriptSet[type[Accessor]]
        self.dataminer_classes:        ScriptSet[type[Dataminer]]
        self.delegate_classes:         ScriptSet[type[Delegate]]
        self.serializer_classes:       ScriptSet[type[Serializer]]
        self.version_provider_classes: ScriptSet[type[VersionProvider]]

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
        all_component_groups = parse_all_component_groups(all_domains)
        for domain in all_domains:
            domain.set_values(all_component_groups[domain.name])
        self.is_imported = True
        memory_usage.add_domain(self)

    def import_scripts(self) -> None:
        # update TypeStuffs
        self.scripts = Scripts(self)
        self.json_decoder = CustomJson.get_special_decoder(self)
        self.json_encoder = CustomJson.get_special_encoder(self)
        self.callables = ScriptImporter.import_scripted_objects("normalizers/", self, functions, callable, "callable")
        self.accessor_classes = ScriptImporter.import_scripted_types("accessors/", self, BUILT_IN_ACCESSOR_CLASSES, Accessor)
        self.dataminer_classes = ScriptImporter.import_scripted_types("dataminers/", self, BUILT_IN_DATAMINER_CLASSES, Dataminer)
        self.delegate_classes = ScriptImporter.import_scripted_types("delegates", self, BUILT_IN_DELEGATE_CLASSES, Delegate)
        self.serializer_classes = ScriptImporter.import_scripted_types("serializers/", self, BUILT_IN_SERIALIZER_CLASSES, Serializer)
        self.version_provider_classes = ScriptImporter.import_scripted_types("version_providers", self, BUILT_IN_VERSION_PROVIDER_CLASSES, VersionProvider)

    def set_values(self, component_groups:dict[str,Any]) -> None:
        self.accessor_types = component_groups["accessor_types"]
        self.dataminer_collections = component_groups["dataminer_collections"]
        self.latest_slots = component_groups["latest_slots"]
        self.logs = component_groups["logs"]
        self.serializers = component_groups["serializers"]
        self.structures = {component_group_name: component_group for component_group_name, component_group in component_groups.items() if component_group_name.startswith("structures/")}
        self.structure_tags = component_groups["structure_tags"]
        self.tablifiers = component_groups["tablifiers"]
        self.version_file_types = component_groups["version_file_types"]
        self.version_tags_order = component_groups["version_tags_order"]
        self.version_tags = component_groups["version_tags"]
        self.versions = component_groups["versions"]

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
