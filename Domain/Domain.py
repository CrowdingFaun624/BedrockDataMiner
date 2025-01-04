import json
from pathlib import Path
from typing import TYPE_CHECKING

import Component.Importer as Importer
import Component.ScriptImporter as ScriptImporter
import Dataminer.BuiltIns.AllFilesDataminer as AllFilesDataminer
import Dataminer.BuiltIns.GrabMultipleFilesDataminer as GrabMultipleFilesDataminer
import Dataminer.BuiltIns.GrabReFilesDataminer as GrabReFilesDataminer
import Dataminer.BuiltIns.GrabSingleFileDataminer as GrabSingleFileDataminer
import Dataminer.BuiltIns.SingleFileDataminer as SingleFileDataminer
import Dataminer.BuiltIns.TagSearcherDataminer as TagSearcherDataminer
import Dataminer.Dataminer as Dataminer
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
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Utilities.Scripts as Scripts
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

class LibFiles():

    def __init__(self, domain:"Domain") -> None:
        self.domain = domain

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} of {self.domain.name}>"

    def __getitem__(self, name:str) -> Path:
        path = self.domain.lib_directory.joinpath(name)
        if not path.exists():
            raise Exceptions.LibFileNotFoundError(name, path)
        elif self.domain.lib_directory not in path.parents:
            raise Exceptions.LibFileWrongDirectoryError(name, path, self.domain.lib_directory)
        else:
            return path

    def get[A](self, name:str, default:A=None, wrong_directory_okay:bool=False) -> Path|A:
        path = self.domain.lib_directory.joinpath(name)
        if not path.exists():
            return default
        elif (wrong_directory := self.domain.lib_directory not in path.parents) and wrong_directory_okay:
            return default
        elif wrong_directory and not wrong_directory_okay:
            raise Exceptions.LibFileWrongDirectoryError(name, path, self.domain.lib_directory)
        else:
            return path

class Domain():

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
        self.assets_directory.mkdir(exist_ok=True)
        self.data_directory.mkdir(exist_ok=True)
        self.lib_directory.mkdir(exist_ok=True)
        self.log_directory.mkdir(exist_ok=True)
        self.scripts_directory.mkdir(exist_ok=True)
        self.structures_directory.mkdir(exist_ok=True)
        self.version_tags_directory.mkdir(exist_ok=True)
        self.versions_directory.mkdir(exist_ok=True)
        self.comparisons_directory.mkdir(exist_ok=True)

        self._accessor_types:dict[str,"AccessorType.AccessorType"]|None = None
        self._dataminer_collections:dict[str,"AbstractDataminerCollection.AbstractDataminerCollection"]|None = None
        self._latest_slots:list[str]|None = None
        self._logs:dict[str,"Log.Log"]|None = None
        self._serializers:dict[str,"Serializer.Serializer"]|None = None
        self._structures:dict[str,"StructureBase.StructureBase"]|None = None
        self._structure_tags:dict[str,"StructureTag.StructureTag"]|None = None
        self._tablifiers:dict[str,"Tablifier.Tablifier"]|None = None
        self._version_file_types:dict[str,"VersionFileType.VersionFileType"]|None = None
        self._version_tags_order:"VersionTagOrder.VersionTagOrder|None" = None
        self._version_tags:dict[str,"VersionTag.VersionTag"]|None = None
        self._versions:dict[str,"Version.Version"]|None = None

        self.data_files = {path.stem: DataFile.DataFile(path) for path in self.data_directory.iterdir()}
        '''
        dictionary of files in the `./_assets/data` directory without the final suffix.
        '''
        self._json_decoder:             type[json.JSONDecoder]|None = None
        self._json_encoder:             type[json.JSONEncoder]|None = None
        self._scripts:                  Scripts.Scripts|None = None
        self._accessor_classes:         ScriptImporter.ScriptSet[type[Accessor.Accessor]]|None = None
        self._dataminer_classes:        ScriptImporter.ScriptSet[type[Dataminer.Dataminer]]|None = None
        self._delegate_classes:         ScriptImporter.ScriptSet[type[Delegate.Delegate]]|None = None
        self._serializer_classes:       ScriptImporter.ScriptSet[type[Serializer.Serializer]]|None = None
        self._version_provider_classes: ScriptImporter.ScriptSet[type[VersionProvider.VersionProvider]]|None = None

        self.lib_files = LibFiles(self)

    def import_components(self) -> None:
        self._scripts = Scripts.Scripts(self)

        self._json_decoder = CustomJson.get_special_decoder(self)
        self._json_encoder = CustomJson.get_special_encoder(self)
        self._accessor_classes = ScriptImporter.import_scripted_types("accessors/", self, BUILT_IN_ACCESSOR_CLASSES, Accessor.Accessor)
        self._dataminer_classes = ScriptImporter.import_scripted_types("dataminers/", self, BUILT_IN_DATAMINER_CLASSES, Dataminer.Dataminer)
        self._delegate_classes = ScriptImporter.import_scripted_types("delegates", self, BUILT_IN_DELEGATE_CLASSES, Delegate.Delegate)
        self._serializer_classes = ScriptImporter.import_scripted_types("serializers/", self, BUILT_IN_SERIALIZER_CLASSES, Serializer.Serializer)
        self._version_provider_classes = ScriptImporter.import_scripted_types("version_providers", self, BUILT_IN_VERSION_PROVIDER_CLASSES, VersionProvider.VersionProvider)

        all_component_groups = Importer.parse_all_component_groups(self)
        self._accessor_types = all_component_groups["accessor_types"]
        self._dataminer_collections = all_component_groups["dataminer_collections"]
        self._latest_slots = all_component_groups["latest_slots"]
        self._logs = all_component_groups["logs"]
        self._serializers = all_component_groups["serializers"]
        self._structures = {component_group_name: component_group for component_group_name, component_group in all_component_groups.items() if component_group_name.startswith("structure/")}
        self._structure_tags = all_component_groups["structure_tags"]
        self._tablifiers = all_component_groups["tablifiers"]
        self._version_file_types = all_component_groups["version_file_types"]
        self._version_tags_order = all_component_groups["version_tags_order"]
        self._version_tags = all_component_groups["version_tags"]
        self._versions = all_component_groups["versions"]

    def get_comparison_file_path(self, name:str, number:int) -> Path:
        comparison_subdirectory = self.comparisons_directory.joinpath(name)
        comparison_subdirectory.mkdir(exist_ok=True)
        return comparison_subdirectory.joinpath(f"report_{str(number).zfill(4)}.txt")

    @property
    def scripts(self) -> "Scripts.Scripts":
        if self._scripts is None:
            self.import_components()
        assert self._scripts is not None
        return self._scripts

    @property
    def json_decoder(self) -> type[json.JSONDecoder]:
        if self._json_decoder is None:
            self.import_components()
        assert self._json_decoder is not None
        return self._json_decoder

    @property
    def json_encoder(self) -> type[json.JSONEncoder]:
        if self._json_encoder is None:
            self.import_components()
        assert self._json_encoder is not None
        return self._json_encoder

    @property
    def accessor_classes(self) -> ScriptImporter.ScriptSet[type[Accessor.Accessor]]:
        if self._accessor_classes is None:
            self.import_components()
        assert self._accessor_classes is not None
        return self._accessor_classes

    @property
    def dataminer_classes(self) -> ScriptImporter.ScriptSet[type[Dataminer.Dataminer]]:
        if self._dataminer_classes is None:
            self.import_components()
        assert self._dataminer_classes is not None
        return self._dataminer_classes

    @property
    def delegate_classes(self) -> ScriptImporter.ScriptSet[type[Delegate.Delegate]]:
        if self._delegate_classes is None:
            self.import_components()
        assert self._delegate_classes is not None
        return self._delegate_classes

    @property
    def serializer_classes(self) -> ScriptImporter.ScriptSet[type[Serializer.Serializer]]:
        if self._serializer_classes is None:
            self.import_components()
        assert self._serializer_classes is not None
        return self._serializer_classes

    @property
    def version_provider_classes(self) -> ScriptImporter.ScriptSet[type[VersionProvider.VersionProvider]]:
        if self._version_provider_classes is None:
            self.import_components()
        assert self._version_provider_classes is not None
        return self._version_provider_classes

    @property
    def accessor_types(self) -> dict[str,"AccessorType.AccessorType"]:
        if self._accessor_types is None:
            self.import_components()
        assert self._accessor_types is not None
        return self._accessor_types

    @property
    def dataminer_collections(self) -> dict[str,"AbstractDataminerCollection.AbstractDataminerCollection"]:
        if self._dataminer_collections is None:
            self.import_components()
        assert self._dataminer_collections is not None
        return self._dataminer_collections

    @property
    def latest_slots(self) -> list[str]:
        if self._latest_slots is None:
            self.import_components()
        assert self._latest_slots is not None
        return self._latest_slots

    @property
    def logs(self) -> dict[str,"Log.Log"]:
        if self._logs is None:
            self.import_components()
        assert self._logs is not None
        return self._logs

    @property
    def serializers(self) -> dict[str,"Serializer.Serializer"]:
        if self._serializers is None:
            self.import_components()
        assert self._serializers is not None
        return self._serializers

    @property
    def structures(self) -> dict[str,"StructureBase.StructureBase"]:
        if self._structures is None:
            self.import_components()
        assert self._structures is not None
        return self._structures

    @property
    def structure_tags(self) -> dict[str,"StructureTag.StructureTag"]:
        if self._structure_tags is None:
            self.import_components()
        assert self._structure_tags is not None
        return self._structure_tags

    @property
    def tablifiers(self) -> dict[str,"Tablifier.Tablifier"]:
        if self._tablifiers is None:
            self.import_components()
        assert self._tablifiers is not None
        return self._tablifiers

    @property
    def version_file_types(self) -> dict[str,"VersionFileType.VersionFileType"]:
        if self._version_file_types is None:
            self.import_components()
        assert self._version_file_types is not None
        return self._version_file_types

    @property
    def version_tags_order(self) -> "VersionTagOrder.VersionTagOrder":
        if self._version_tags_order is None:
            self.import_components()
        assert self._version_tags_order is not None
        return self._version_tags_order

    @property
    def version_tags(self) -> dict[str,"VersionTag.VersionTag"]:
        if self._version_tags is None:
            self.import_components()
        assert self._version_tags is not None
        return self._version_tags

    @property
    def versions(self) -> dict[str,"Version.Version"]:
        if self._versions is None:
            self.import_components()
        assert self._versions is not None
        return self._versions

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"
