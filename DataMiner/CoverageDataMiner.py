import re

import Component.Importer as Importer
import DataMiner.AbstractDataMinerCollection as AbstractDataMinerCollection
import DataMiner.DataMiner as DataMiner
import DataMiner.DataMinerCollection as DataMinerCollection
import DataMiner.DataMinerEnvironment as DataMinerEnvironment
import DataMiner.FileDataMiner as FileDataMiner
import Structure.StructureBase as StructureBase
import Version.Version as Version


class CoverageDataMiner(AbstractDataMinerCollection.AbstractDataMinerCollection):

    def __init__(
        self,
        file_name:str,
        name:str,
        comparing_disabled:bool,
        remove_files:set[str],
        remove_regex:list[re.Pattern[str]],
        remove_prefixes:list[str],
        remove_suffixes:list[str],
    ) -> None:
        super().__init__(file_name, name, comparing_disabled)
        self.remove_files = remove_files
        self.remove_regex = remove_regex
        self.remove_prefixes = remove_prefixes
        self.remove_suffixes = remove_suffixes

        self.file_list_dataminer:AbstractDataMinerCollection.AbstractDataMinerCollection|None = None

    def link_subcomponents(self, file_list_dataminer:AbstractDataMinerCollection.AbstractDataMinerCollection, structure: StructureBase.StructureBase) -> None:
        super().link_subcomponents(structure)
        self.file_list_dataminer = file_list_dataminer

    def get_dependencies(self, version: Version.Version) -> list[DataMinerCollection.DataMinerCollection]:
        return [
            dataminer_collection for dataminer_collection in Importer.dataminer_collections.values()
            if dataminer_collection is not self
            if isinstance(dataminer_collection, DataMinerCollection.DataMinerCollection)
            if (dataminer := dataminer_collection.get_dataminer_class(version)) is not None
            if issubclass(dataminer, FileDataMiner.FileDataMiner)
        ]

    def supports_version(self, version: Version.Version) -> bool:
        assert self.file_list_dataminer is not None
        return self.file_list_dataminer.supports_version(version)

    def do_dataminer_collection(
        self,
        dataminer_collection:DataMinerCollection.DataMinerCollection,
        version:Version.Version,
        environment:DataMinerEnvironment.DataMinerEnvironment,
        file_set:FileDataMiner.FileSet,
        version_files_covered:set[str],
        version_files_covered_dict:dict[DataMiner.DataMiner,set[str]],
    ) -> None:
        dataminer = dataminer_collection.get_dataminer(version)
        assert isinstance(dataminer, FileDataMiner.FileDataMiner)
        dataminer_files_covered = dataminer.get_coverage(file_set, environment)
        # because this thing says that its dependencies are every single
        # DataMinerCollection, the dependencies of all of its dependencies are
        # already fulfilled. Truly a wonderful advantage of having Coverage be
        # a type of DataMinerCollection.
        if len(overlapping_files := version_files_covered.intersection(dataminer_files_covered)) > 0:
            other_dataminers = [
                other_dataminer
                for other_dataminer, other_dataminer_coverage in version_files_covered_dict.items()
                if len(other_dataminer_coverage.intersection(dataminer_files_covered)) > 0
            ]
            raise RuntimeError(f"The following files in {version} are covered by {dataminer} and dataminers [{", ".join(repr(other_dataminer) for other_dataminer in other_dataminers)}]: [{", ".join(overlapping_files)}]")
        version_files_covered.update(dataminer_files_covered)
        version_files_covered_dict[dataminer] = dataminer_files_covered

    def datamine(self, version: Version.Version, environment: DataMinerEnvironment.DataMinerEnvironment) -> list[str]:
        assert self.file_list_dataminer is not None
        file_set_list:dict[str,str] = self.file_list_dataminer.get_data_file(version)
        file_set_set = set(file_set_list)
        file_set = FileDataMiner.FileSet(file_set_list)
        version_files_covered:set[str] = set()
        version_files_covered_dict:dict[DataMiner.DataMiner,set[str]] = {}
        for dataminer_collection in self.get_dependencies(version):
            self.do_dataminer_collection(dataminer_collection, version, environment, file_set, version_files_covered, version_files_covered_dict)
        leftover_files = file_set_set - version_files_covered
        # comparison
        current_set = leftover_files
        current_set -= self.remove_files
        current_set = {item for item in current_set if not any(item.endswith(suffix) for suffix in self.remove_suffixes) and not any(item.startswith(prefix) for prefix in self.remove_prefixes)}
        current_set = {item for item in current_set if not any(pattern.fullmatch(item) for pattern in self.remove_regex)}
        return sorted(current_set)
