import re
from typing import AbstractSet, Iterable, Sequence

from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Dataminer.Dataminer import Dataminer
from Dataminer.DataminerCollection import DataminerCollection
from Dataminer.DataminerEnvironment import DataminerEnvironment
from Dataminer.FileDataminer import FileDataminer, FileSet
from Structure.StructureInfo import StructureInfo
from Version.Version import Version
from Version.VersionFileType import VersionFileType


def convert_to_set(data:str|Sequence[str]) -> AbstractSet[str]:
    return {data} if isinstance(data, str) else set(data)

def convert_to_sequence(data:str|Sequence[str]) -> Sequence[re.Pattern]:
    return (re.compile(data),) if isinstance(data, str) else [re.compile(pattern) for pattern in data]

class CoverageDataminer(AbstractDataminerCollection):

    __slots__ = (
        "file",
        "file_list_dataminer",
        "remove_files_list",
        "remove_files",
        "remove_prefixes_list",
        "remove_prefixes",
        "remove_regex_list",
        "remove_regex",
        "remove_suffixes_list",
        "remove_suffixes",
        "structure_info",
    )

    def link_coverage_dataminer_collection(
        self,
        file:VersionFileType,
        file_list_dataminer:AbstractDataminerCollection,
        remove_files:Sequence[str],
        remove_regex:Sequence[str],
        remove_prefixes:Sequence[str],
        remove_suffixes:Sequence[str],
        structure_info:StructureInfo,
    ) -> None:
        self.file = file
        self.file_list_dataminer = file_list_dataminer
        self.remove_files_list = remove_files
        self.remove_regex_list = remove_regex
        self.remove_prefixes_list = remove_prefixes
        self.remove_suffixes_list = remove_suffixes
        self.structure_info = structure_info

    def finalize_coverage_dataminer(self) -> None:
        self.remove_files = convert_to_set(self.remove_files_list)
        self.remove_regex = convert_to_sequence(self.remove_regex_list)
        self.remove_prefixes = convert_to_set(self.remove_prefixes_list)
        self.remove_suffixes = convert_to_set(self.remove_suffixes_list)

    def get_structure_info(self, version: Version) -> StructureInfo:
        return self.structure_info

    def get_required_dependencies(self, version: Version) -> Iterable[DataminerCollection]:
        return (
            dataminer_collection for dataminer_collection in self.domain.dataminer_collections.values()
            if dataminer_collection is not self
            if isinstance(dataminer_collection, DataminerCollection)
            if self.file in (dataminer_settings := dataminer_collection.get_dataminer_settings(version)).version_file_types
            if (dataminer := dataminer_collection.get_dataminer_class(version)) is not None
            if issubclass(dataminer, FileDataminer)
        )

    def get_optional_dependencies(self, version: Version) -> Iterable[AbstractDataminerCollection]:
        return ()

    def supports_version(self, version: Version) -> bool:
        return self.file_list_dataminer.supports_version(version)

    def do_dataminer_collection(
        self,
        dataminer_collection:DataminerCollection,
        version:Version,
        environment:DataminerEnvironment,
        file_set:FileSet,
        version_files_covered:set[str],
        version_files_covered_dict:dict[Dataminer,set[str]],
    ) -> None:
        dataminer = dataminer_collection.get_dataminer(version)
        assert isinstance(dataminer, FileDataminer)
        dataminer_files_covered = dataminer.get_coverage(file_set, environment)
        # because this thing says that its dependencies are every single
        # DataminerCollection, the dependencies of all of its dependencies are
        # already fulfilled. Truly a wonderful advantage of having Coverage be
        # a type of DataminerCollection.
        if len(overlapping_files := version_files_covered.intersection(dataminer_files_covered)) > 0:
            other_dataminers = (
                other_dataminer
                for other_dataminer, other_dataminer_coverage in version_files_covered_dict.items()
                if len(other_dataminer_coverage.intersection(dataminer_files_covered)) > 0
            )
            raise RuntimeError(f"The following files in {version} are covered by {dataminer} and dataminers [{", ".join(repr(other_dataminer) for other_dataminer in other_dataminers)}]: [{", ".join(overlapping_files)}]")
        version_files_covered.update(dataminer_files_covered)
        version_files_covered_dict[dataminer] = dataminer_files_covered

    def datamine(self, version: Version, environment: DataminerEnvironment) -> list[str]:
        file_set_list:dict[str,str] = self.file_list_dataminer.get_data_file(version)
        file_set_set = set(file_set_list)
        file_set = FileSet(file_set_list)
        version_files_covered:set[str] = set()
        version_files_covered_dict:dict[Dataminer,set[str]] = {}
        for dataminer_collection in self.get_required_dependencies(version):
            self.do_dataminer_collection(dataminer_collection, version, environment, file_set, version_files_covered, version_files_covered_dict)
        leftover_files = file_set_set - version_files_covered
        # comparison
        current_set = leftover_files
        current_set -= self.remove_files
        current_set = {item for item in current_set if not any(item.endswith(suffix) for suffix in self.remove_suffixes) and not any(item.startswith(prefix) for prefix in self.remove_prefixes)}
        current_set = {item for item in current_set if not any(pattern.fullmatch(item) for pattern in self.remove_regex)}
        return sorted(current_set)
