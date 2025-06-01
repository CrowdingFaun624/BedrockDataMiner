from pathlib import Path
from types import EllipsisType
from typing import Any, Iterable, Sequence

import Component.Component as Component
import Component.Dataminer.AbstractDataminerCollectionComponent as AbstractDataminerCollectionComponent
import Component.Dataminer.DataminerCollectionComponent as DataminerCollectionComponent
import Component.ImporterEnvironment as ImporterEnvironment
import Dataminer.AbstractDataminerCollection as AbstractDataminerCollection
import Dataminer.DataminerCollection as DataminerCollection
import Dataminer.DataminerSettings as DataminerSettings
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace
import Version.Version as Version


class DataminerImporterEnvironment(ImporterEnvironment.ImporterEnvironment[dict[str,AbstractDataminerCollection.AbstractDataminerCollection]]):

    assume_type = DataminerCollectionComponent.DataminerCollectionComponent.class_name

    __slots__ = ()

    def get_component_files(self) -> Iterable[Path]:
        return (self.domain.dataminer_collections_file,)

    def get_component_group_name(self, file_path:Path) -> str:
        return "dataminer_collections"

    def get_output(self, components: dict[str, AbstractDataminerCollectionComponent.AbstractDataminerCollectionComponent], name: str, trace:Trace.Trace) -> dict[str, AbstractDataminerCollection.AbstractDataminerCollection]|EllipsisType:
        with trace.enter(self, name, ...):
            return {component_name: component.final for component_name, component in components.items() if not component.disabled}
        return ...

    def get_assumed_used_components(self, components: dict[str, Component.Component], name:str, trace:Trace.Trace) -> Iterable[Component.Component]:
        with trace.enter(self, name, ...):
            return components.values()
        return ()

    def get_dependencies(self, dataminer_settings:DataminerSettings.DataminerSettings, dataminer_settings_dict:dict[DataminerCollection.DataminerCollection,DataminerSettings.DataminerSettings], already:set[str]) -> Sequence[str]:
        if dataminer_settings.name in already:
            return (dataminer_settings.name,)
        already.add(dataminer_settings.name)
        duplicated_dataminer_settings:list[str] = []
        for dependency in dataminer_settings.dependencies:
            if not isinstance(dependency, DataminerCollection.DataminerCollection):
                # if it's not a DataminerCollection, its dependencies cannot vary on version.
                continue
            already_copy = already.copy()
            duplicated_dataminer_settings.extend(self.get_dependencies(dataminer_settings_dict[dependency], dataminer_settings_dict, already_copy))
        return duplicated_dataminer_settings

    def check_for_loops(self, used_versions:set[Version.Version], dataminer_collections:list[AbstractDataminerCollection.AbstractDataminerCollection], trace:Trace.Trace) -> None:
        '''Raises an error if a loop exists in any part.'''
        versions = sorted(used_versions)
        for version in versions:
            all_dataminer_settings = {dataminer_collection: dataminer_collection.get_dataminer_settings(version) for dataminer_collection in dataminer_collections if isinstance(dataminer_collection, DataminerCollection.DataminerCollection)}
            trace.exceptions(
                Exceptions.DataminerSettingsImporterLoopError(dataminer_settings, duplicated_datminer_settings)
                for dataminer_settings in all_dataminer_settings.values()
                if len(duplicated_datminer_settings := self.get_dependencies(dataminer_settings, all_dataminer_settings, set())) > 0
            )

    def check_for_duplicate_file_names(self, dataminers:dict[str,AbstractDataminerCollection.AbstractDataminerCollection], trace:Trace.Trace) -> None:
        names:dict[str,AbstractDataminerCollection.AbstractDataminerCollection] = {}
        duplicate_name_groups:dict[str,list[AbstractDataminerCollection.AbstractDataminerCollection]] = {}
        for dataminer in dataminers.values():
            if dataminer.file_name in names:
                if dataminer.file_name not in duplicate_name_groups:
                    duplicate_name_groups[dataminer.file_name] = [names[dataminer.file_name]]
                duplicate_name_groups[dataminer.file_name].append(dataminer)
            else:
                names[dataminer.file_name] = dataminer
        trace.exceptions(
            Exceptions.DataminerDuplicateFileNameError(name, duplicate_dataminers)
            for name, duplicate_dataminers in duplicate_name_groups.items()
        )

    def check(self, output: dict[str,AbstractDataminerCollection.AbstractDataminerCollection], other_outputs:dict[str,Any], name:str, trace:Trace.Trace) -> None:
        with trace.enter(self, name, ...):
            super().check(output, other_outputs, name, trace)
            used_versions:set[Version.Version] = set()
            for dataminer_collection in output.values():
                if not isinstance(dataminer_collection, DataminerCollection.DataminerCollection):
                    continue
                for dataminer_settings in dataminer_collection.dataminer_settings:
                    start_version = dataminer_settings.version_range.start
                    stop_version = dataminer_settings.version_range.stop
                    if start_version is not None:
                        used_versions.add(start_version)
                    if stop_version is not None:
                        used_versions.add(stop_version)
            self.check_for_loops(used_versions, list(output.values()), trace)
            self.check_for_duplicate_file_names(output, trace)
