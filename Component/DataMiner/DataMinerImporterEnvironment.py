from pathlib import Path
from typing import Any, Iterable

import Component.Component as Component
import Component.DataMiner.AbstractDataMinerCollectionComponent as AbstractDataMinerCollectionComponent
import Component.DataMiner.DataMinerCollectionComponent as DataMinerCollectionComponent
import Component.ImporterEnvironment as ImporterEnvironment
import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection
import DataMiner.DataMinerCollection as DataMinerCollection
import DataMiner.DataMinerSettings as DataMinerSettings
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Version.Version as Version


class DataMinerImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,AbstractDataMinerCollection.AbstractDataMinerCollection]]):

    assume_type = DataMinerCollectionComponent.DataMinerCollectionComponent.class_name

    def get_imports(self, components:dict[str,Component.Component], all_components:dict[str,dict[str,Component.Component]], name:str) -> dict[str,dict[str,Component.Component]]:
        imports = {component_group_name: component_group for component_group_name, component_group in all_components.items() if component_group_name.startswith("structures/")}
        imports.update({"versions": all_components["versions"], "version_file_types": all_components["version_file_types"], "serializers": all_components["serializers"]})
        return imports

    def get_component_files(self) -> Iterable[Path]:
        return [FileManager.DATAMINER_COLLECTIONS_FILE]

    def get_component_group_name(self, file_path:Path) -> str:
        return "dataminer_collections"

    def get_output(self, components: dict[str, AbstractDataMinerCollectionComponent.AbstractDataMinerCollectionComponent], name: str) -> dict[str, AbstractDataMinerCollection.AbstractDataMinerCollection]:
        return {component_name: component.get_final() for component_name, component in components.items() if not component.disabled}

    def get_assumed_used_components(self, components: dict[str, Component.Component], name:str) -> Iterable[Component.Component]:
        return components.values()

    def get_dependencies(self, dataminer_settings:DataMinerSettings.DataMinerSettings, dataminer_settings_dict:dict[DataMinerCollection.DataMinerCollection,DataMinerSettings.DataMinerSettings], already:set[str]) -> list[str]:
        if dataminer_settings.get_name() in already:
            return [dataminer_settings.get_name()]
        already.add(dataminer_settings.get_name())
        duplicated_dataminer_settings:list[str] = []
        for dependency in dataminer_settings.get_dependencies():
            if not isinstance(dependency, DataMinerCollection.DataMinerCollection):
                # if it's not a DataMinerCollection, its dependencies cannot vary on version.
                continue
            already_copy = already.copy()
            duplicated_dataminer_settings.extend(self.get_dependencies(dataminer_settings_dict[dependency], dataminer_settings_dict, already_copy))
        return duplicated_dataminer_settings

    def check_for_loops(self, used_versions:set[Version.Version], dataminer_collections:list[AbstractDataMinerCollection.AbstractDataMinerCollection]) -> list[Exception]:
        '''Raises an error if a loop exists in any part.'''
        versions = sorted(used_versions)
        exceptions:list[Exception] = []
        for version in versions:
            all_dataminer_settings = {dataminer_collection: dataminer_collection.get_dataminer_settings(version) for dataminer_collection in dataminer_collections if isinstance(dataminer_collection, DataMinerCollection.DataMinerCollection)}
            exceptions.extend(
                Exceptions.DataMinerSettingsImporterLoopError(dataminer_settings, duplicated_datminer_settings)
                for dataminer_settings in all_dataminer_settings.values()
                if len(duplicated_datminer_settings := self.get_dependencies(dataminer_settings, all_dataminer_settings, set())) > 0
            )
        return exceptions

    def check_for_duplicate_file_names(self, dataminers:dict[str,AbstractDataMinerCollection.AbstractDataMinerCollection]) -> list[Exception]:
        names:dict[str,AbstractDataMinerCollection.AbstractDataMinerCollection] = {}
        duplicate_name_groups:dict[str,list[AbstractDataMinerCollection.AbstractDataMinerCollection]] = {}
        for dataminer in dataminers.values():
            if dataminer.file_name in names:
                if dataminer.file_name not in duplicate_name_groups:
                    duplicate_name_groups[dataminer.file_name] = [names[dataminer.file_name]]
                duplicate_name_groups[dataminer.file_name].append(dataminer)
            else:
                names[dataminer.file_name] = dataminer
        return [
            Exceptions.DataMinerDuplicateFileNameError(name, duplicate_dataminers)
            for name, duplicate_dataminers in duplicate_name_groups.items()
        ]

    def check(self, output: dict[str,AbstractDataMinerCollection.AbstractDataMinerCollection], other_outputs:dict[str,Any]) -> list[Exception]:
        exceptions = super().check(output, other_outputs)
        used_versions:set[Version.Version] = set()
        for dataminer_collection in output.values():
            if not isinstance(dataminer_collection, DataMinerCollection.DataMinerCollection):
                continue
            for dataminer_settings in dataminer_collection.get_all_dataminer_settings():
                start_version = dataminer_settings.get_version_range().start
                stop_version = dataminer_settings.get_version_range().stop
                if start_version is not None:
                    used_versions.add(start_version)
                if stop_version is not None:
                    used_versions.add(stop_version)
        exceptions.extend(self.check_for_loops(used_versions, list(output.values())))
        exceptions.extend(self.check_for_duplicate_file_names(output))
        return exceptions
