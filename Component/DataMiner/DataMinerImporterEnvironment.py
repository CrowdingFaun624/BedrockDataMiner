from typing import Any, Iterable

from pathlib2 import Path

import Component.Component as Component
import Component.DataMiner.DataMinerCollectionComponent as DataMinerCollectionComponent
import Component.ImporterEnvironment as ImporterEnvironment
import DataMiner.DataMinerCollection as DataMinerCollection
import DataMiner.DataMinerSettings as DataMinerSettings
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager
import Version.Version as Version


class DataMinerImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,DataMinerCollection.DataMinerCollection]]):

    assume_type = DataMinerCollectionComponent.DataMinerCollectionComponent.class_name

    def get_imports(self, components:dict[str,Component.Component], all_components:dict[str,dict[str,Component.Component]], name:str) -> dict[str,dict[str,Component.Component]]:
        return {component_group_name: component_group for component_group_name, component_group in all_components.items() if component_group_name.startswith("structures/")}

    def get_component_files(self) -> Iterable[Path]:
        return [FileManager.DATAMINER_COLLECTIONS_FILE]

    def get_component_group_name(self, file_path:Path) -> str:
        return "dataminer_collections"

    def get_dependencies(self, dataminer_settings:DataMinerSettings.DataMinerSettings, dataminer_settings_dict:dict[DataMinerCollection.DataMinerCollection,DataMinerSettings.DataMinerSettings], already:set[str]) -> list[str]:
        if dataminer_settings.get_name() in already:
            return [dataminer_settings.get_name()]
        already.add(dataminer_settings.get_name())
        duplicated_dataminer_settings:list[str] = []
        for dependency in dataminer_settings.get_dependencies():
            already_copy = already.copy()
            duplicated_dataminer_settings.extend(self.get_dependencies(dataminer_settings_dict[dependency], dataminer_settings_dict, already_copy))
        return duplicated_dataminer_settings

    def check_for_loops(self, used_versions:set[Version.Version], dataminer_collections:list[DataMinerCollection.DataMinerCollection]) -> list[Exception]:
        '''Raises an error if a loop exists in any part.'''
        versions = sorted(used_versions)
        exceptions:list[Exception] = []
        for version in versions:
            all_dataminer_settings = {dataminer_collection: dataminer_collection.get_dataminer_settings(version) for dataminer_collection in dataminer_collections}
            for dataminer_settings in all_dataminer_settings.values():
                duplicated_datminer_settings = self.get_dependencies(dataminer_settings, all_dataminer_settings, set())
                if len(duplicated_datminer_settings) > 0:
                    exceptions.append(Exceptions.DataMinerSettingsImporterLoopError(dataminer_settings, duplicated_datminer_settings))
        return exceptions

    def check(self, output: dict[str,DataMinerCollection.DataMinerCollection], other_outputs:dict[str,Any]) -> list[Exception]:
        exceptions = super().check(output, other_outputs)
        used_versions:set[Version.Version] = set()
        for dataminer_collection in output.values():
            for dataminer_settings in dataminer_collection.get_all_dataminer_settings():
                if dataminer_settings.version_range.start is not None:
                    used_versions.add(dataminer_settings.version_range.start)
                if dataminer_settings.version_range.stop is not None:
                    used_versions.add(dataminer_settings.version_range.stop)
        exceptions.extend(self.check_for_loops(used_versions, list(output.values())))
        return exceptions
