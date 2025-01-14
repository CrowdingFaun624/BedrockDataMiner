import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, NotRequired, TypedDict

import Component.ComponentFunctions as ComponentFunctions
import Component.Importer as Importer
import Component.ScriptImporter as ScriptImporter
import Component.Types as Types
import Dataminer.BuiltIns.AllFilesDataminer as AllFilesDataminer
import Dataminer.BuiltIns.GrabMultipleFilesDataminer as GrabMultipleFilesDataminer
import Dataminer.BuiltIns.GrabReFilesDataminer as GrabReFilesDataminer
import Dataminer.BuiltIns.GrabSingleFileDataminer as GrabSingleFileDataminer
import Dataminer.BuiltIns.SingleFileDataminer as SingleFileDataminer
import Dataminer.BuiltIns.TagSearcherDataminer as TagSearcherDataminer
import Dataminer.Dataminer as Dataminer
import Domain.Domains as Domains
import Domain.LibFiles as LibFiles
import Downloader.Accessor as Accessor
import Downloader.DownloadAccessor as DownloadAccessor
import Downloader.DummyAccessor as DummyAccessor
import Downloader.SingleDirectoryFileAccessor as SingleDirectoryFileAccessor
import Downloader.StoredAccessor as StoredAccessor
import Downloader.ZipAccessor as ZipAccessor
import Serializer.CustomJsonSerializer as CustomJsonSerializer
import Serializer.DummySerializer as DummySerializer
import Serializer.JsonSerializer as JsonSerializer
import Serializer.LinesSerializer as LinesSerializer
import Serializer.RepairableJsonSerializer as RepairableJsonSerializer
import Serializer.Serializer as Serializer
import Serializer.TextSerializer as TextSerializer
import Structure.Delegate.DefaultBaseDelegate as DefaultBaseDelegate
import Structure.Delegate.DefaultDelegate as DefaultDelegate
import Structure.Delegate.Delegate as Delegate
import Structure.Delegate.LongStringDelegate as LongStringDelegate
import Utilities.CustomJson as CustomJson
import Utilities.DataFile as DataFile
import Utilities.FileManager as FileManager
import Utilities.Scripts as Scripts
import Utilities.TypeVerifier as TypeVerifier
import Version.VersionProvider.LatestVersionProvider as LatestVersionProvider
import Version.VersionProvider.VersionProvider as VersionProvider

if TYPE_CHECKING:
    import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
    import Downloader.AccessorType as AccessorType
    import Serializer.Serializer as Serializer
    import Structure.StructureBase as StructureBase
    import Structure.StructureTag as StructureTag
    import Tablifier.Tablifier as Tablifier
    import Utilities.Log as Log
    import Version.Version as Version
    import Version.VersionFileType as VersionFileType
    import Version.VersionTag.VersionTag as VersionTag
    import Version.VersionTag.VersionTagOrder as VersionTagOrder

BUILT_IN_ACCESSOR_CLASSES:dict[str,type[Accessor.Accessor]] = {accessor_class.__name__: accessor_class for accessor_class in [
    DownloadAccessor.DownloadAccessor,
    DummyAccessor.DummyAccessor,
    SingleDirectoryFileAccessor.SingleDirectoryFileAccessor,
    StoredAccessor.StoredAccessor,
    ZipAccessor.ZipAccessor,
]}

BUILT_IN_DATAMINER_CLASSES:dict[str,type[Dataminer.Dataminer]] = {dataminer_class.__name__: dataminer_class for dataminer_class in [
    Dataminer.Dataminer,
    AllFilesDataminer.AllFilesDataminer,
    GrabMultipleFilesDataminer.GrabMultipleFilesDataminer,
    GrabReFilesDataminer.GrabReFilesDataminer,
    GrabSingleFileDataminer.GrabSingleFileDataminer,
    SingleFileDataminer.SingleFileDataminer,
    TagSearcherDataminer.TagSearcherDataminer,
]}

BUILT_IN_DELEGATE_CLASSES:dict[str,type[Delegate.Delegate]] = {delegate_type.__name__: delegate_type for delegate_type in [
    Delegate.Delegate,
    DefaultDelegate.DefaultDelegate,
    DefaultBaseDelegate.DefaultBaseDelegate,
    LongStringDelegate.LongStringDelegate,
]}

BUILT_IN_SERIALIZER_CLASSES:dict[str,type[Serializer.Serializer]] = {dataminer_class.__name__: dataminer_class for dataminer_class in [
    CustomJsonSerializer.CustomJsonSerializer,
    DummySerializer.DummySerializer,
    JsonSerializer.JsonSerializer,
    LinesSerializer.LinesSerializer,
    RepairableJsonSerializer.RepairableJsonSerializer,
    Serializer.Serializer,
    TextSerializer.TextSerializer,
]}

BUILT_IN_VERSION_PROVIDER_CLASSES:dict[str,type[VersionProvider.VersionProvider]] = {version_provider_class.__name__: version_provider_class for version_provider_class in [
    LatestVersionProvider.LatestVersionProvider,
]}

class DomainManifestTypedDict(TypedDict):
    aliases: NotRequired[list[str]]
    dependencies: NotRequired[list[str]]
    is_library: NotRequired[bool]

class Domain():

    __slots__ = (
        "all_serializers",
        "accessor_types",
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
        "dependencies",
        "callables",
    )

    def __init__(self, name:str) -> None:
        self.name = name
        self.assets_directory           = FileManager.DOMAINS_DIRECTORY.joinpath(name)
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

        self.is_library:bool
        self.aliases:list[str]
        self.dependencies:list[str]
        self.read_manifest()

        self.accessor_types:dict[str,"AccessorType.AccessorType"]
        self.dataminer_collections:dict[str,"AbstractDataminerCollection.AbstractDataminerCollection"]
        self.latest_slots:list[str]
        self.logs:dict[str,"Log.Log"]
        self.serializers:dict[str,"Serializer.Serializer"]
        self.structures:dict[str,"StructureBase.StructureBase"]
        self.structure_tags:dict[str,"StructureTag.StructureTag"]
        self.tablifiers:dict[str,"Tablifier.Tablifier"]
        self.version_file_types:dict[str,"VersionFileType.VersionFileType"]
        self.version_tags_order:"VersionTagOrder.VersionTagOrder"
        self.version_tags:dict[str,"VersionTag.VersionTag"]
        self.versions:dict[str,"Version.Version"]

        self.data_files = self._get_data_files()
        '''
        dictionary of files in the `./_assets/data` directory without the final suffix.
        '''
        self.json_decoder:             type[json.JSONDecoder]
        self.json_encoder:             type[json.JSONEncoder]
        self.scripts:                  Scripts.Scripts
        self.callables:                ScriptImporter.ScriptSet[Callable]
        self.accessor_classes:         ScriptImporter.ScriptSet[type[Accessor.Accessor]]
        self.dataminer_classes:        ScriptImporter.ScriptSet[type[Dataminer.Dataminer]]
        self.delegate_classes:         ScriptImporter.ScriptSet[type[Delegate.Delegate]]
        self.serializer_classes:       ScriptImporter.ScriptSet[type[Serializer.Serializer]]
        self.version_provider_classes: ScriptImporter.ScriptSet[type[VersionProvider.VersionProvider]]

        self.lib_files = LibFiles.LibFiles(self)
        self.type_stuff = Types.TypeStuff(self)
        self.type_stuff.extend(Types.primary_type_stuff)

    def get_cascading_dependencies(self, memo:set["Domain"]) -> list["Domain"]:
        if self not in memo:
            output:list[Domain] = []
            memo.add(self)
            for dependency_name in self.dependencies:
                dependency = Domains.domains[dependency_name]
                output.extend(dependency.get_cascading_dependencies(memo))
            output.append(self)
            return output
        else:
            return []

    def read_manifest(self) -> None:
        with open(self.domain_file, "rt") as f:
            file:DomainManifestTypedDict = json.load(f)
        TypeVerifier.TypedDictTypeVerifier(
            TypeVerifier.TypedDictKeyTypeVerifier("aliases", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a str", "a list")),
            TypeVerifier.TypedDictKeyTypeVerifier("is_library", "a bool", False, bool),
            TypeVerifier.TypedDictKeyTypeVerifier("dependencies", "a list", False, TypeVerifier.ListTypeVerifier(str, list, "a Domain", "a list")),
        ).base_verify(file, [self])
        self.is_library = file.get("is_library", False)
        self.aliases = file.get("aliases", [])
        self.dependencies = file.get("dependencies", [])

    def import_components(self) -> None:
        all_domains = self.get_cascading_dependencies(set())
        for domain in all_domains:
            for dependency_name in domain.dependencies:
                domain.type_stuff.link(Domains.domains[dependency_name].type_stuff)
        for domain in all_domains:
            domain.import_scripts()
        all_component_groups = Importer.parse_all_component_groups(all_domains)
        for domain in all_domains:
            domain.set_values(all_component_groups[domain.name])

    def import_scripts(self) -> None:
        # update TypeStuffs
        self.scripts = Scripts.Scripts(self)
        self.json_decoder = CustomJson.get_special_decoder(self)
        self.json_encoder = CustomJson.get_special_encoder(self)
        self.callables = ScriptImporter.import_scripted_objects("normalizers/", self, ComponentFunctions.functions, callable, "callable")
        self.accessor_classes = ScriptImporter.import_scripted_types("accessors/", self, BUILT_IN_ACCESSOR_CLASSES, Accessor.Accessor)
        self.dataminer_classes = ScriptImporter.import_scripted_types("dataminers/", self, BUILT_IN_DATAMINER_CLASSES, Dataminer.Dataminer)
        self.delegate_classes = ScriptImporter.import_scripted_types("delegates", self, BUILT_IN_DELEGATE_CLASSES, Delegate.Delegate)
        self.serializer_classes = ScriptImporter.import_scripted_types("serializers/", self, BUILT_IN_SERIALIZER_CLASSES, Serializer.Serializer)
        self.version_provider_classes = ScriptImporter.import_scripted_types("version_providers", self, BUILT_IN_VERSION_PROVIDER_CLASSES, VersionProvider.VersionProvider)

    def set_values(self, component_groups:dict[str,Any]) -> None:
        self.accessor_types = component_groups["accessor_types"]
        self.dataminer_collections = component_groups["dataminer_collections"]
        self.latest_slots = component_groups["latest_slots"]
        self.logs = component_groups["logs"]
        self.serializers = component_groups["serializers"]
        self.structures = {component_group_name: component_group for component_group_name, component_group in component_groups.items() if component_group_name.startswith("structure/")}
        self.structure_tags = component_groups["structure_tags"]
        self.tablifiers = component_groups["tablifiers"]
        self.version_file_types = component_groups["version_file_types"]
        self.version_tags_order = component_groups["version_tags_order"]
        self.version_tags = component_groups["version_tags"]
        self.versions = component_groups["versions"]

        self.all_serializers:dict[str, Serializer.Serializer] = {}
        for dependency_name in self.dependencies:
            dependency = Domains.domains[dependency_name]
            self.all_serializers.update(dependency.serializers)
        self.all_serializers.update(self.serializers)

    def _get_data_files(self) -> dict[str,DataFile.DataFile]:
        if self.data_directory.exists():
            return {path.stem: DataFile.DataFile(path) for path in self.data_directory.iterdir()}
        else:
            return {}

    def get_comparison_file_path(self, name:str, number:int) -> Path:
        comparison_subdirectory = self.comparisons_directory.joinpath(name)
        comparison_subdirectory.mkdir(exist_ok=True)
        return comparison_subdirectory.joinpath(f"report_{str(number).zfill(4)}.txt")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def __hash__(self) -> int:
        return hash(self.name)
