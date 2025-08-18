from types import EllipsisType
from typing import Any, Sequence

import Domain.Domain as Domain
from Component.ComponentObject import ComponentObject
from Dataminer.AbstractDataminerCollection import AbstractDataminerCollection
from Structure.StructureBase import StructureBase
from Structure.StructureEnvironment import (
    ComparisonEnvironment,
    EnvironmentType,
    StructureEnvironment,
)
from Utilities.Exceptions import TablifierError
from Utilities.FileManager import OUTPUT_DIRECTORY
from Utilities.Log import Log
from Utilities.Trace import Trace
from Version.Version import Version
from Version.VersionProvider.VersionProvider import VersionProviderCreator


class Tablifier(ComponentObject):

    __slots__ = (
        "dataminer_collection",
        "file_name",
        "log",
        "path",
        "structure",
        "version_provider",
    )

    def link_tablifier(
        self,
        dataminer_collection:AbstractDataminerCollection,
        file_name:str,
        log: Log | None,
        structure:StructureBase,
        version_provider:VersionProviderCreator,
    ) -> None:
        self.dataminer_collection = dataminer_collection
        self.file_name = file_name
        self.log = log
        self.path = OUTPUT_DIRECTORY.joinpath(self.file_name)
        self.structure = structure
        self.version_provider = version_provider

    def _get_versions_between(self, all_versions:list[Version], versions:list[Version]) -> list[list[Version]]:
        version_index = 0
        between_versions:list[Version] = []
        output:list[list[Version]] = []
        for version in all_versions:
            if version is versions[version_index]:
                output.append(between_versions)
                version_index += 1
                if version_index >= len(versions):
                    break
                continue
            else:
                between_versions.append(version)
        return output

    def print_exception_list(self, trace:Trace, versions:Sequence["Version"], domain:"Domain.Domain") -> bool:
        """
        Prints all exceptions and traces in list and raises an exception at the end if the list has any items.
        """
        texts:list[str] = list(trace.stringify())
        if trace.has_exceptions:
            if self.log is not None and self.log.supports_type(self.log, str):
                self.log.write(f"-------- {trace.exception_count} EXCEPTIONS IN {self.name} ON {", ".join(version.name for version in versions)} --------\n\n")
                self.log.write("\n".join(texts))
            for text in texts:
                print(text)
        return len(trace._exceptions) > 0

    def ensure_not_ellipsis[a](self, data:a|EllipsisType, trace:Trace, versions:Sequence["Version"], domain:"Domain.Domain") -> a:
        if self.print_exception_list(trace, versions, domain) or data is ...:
            raise TablifierError(self)
        else:
            return data

    def tablify(self, all_versions:list[Version], domain:"Domain.Domain") -> None:
        versions = self.version_provider.version_provider.get_versions(all_versions, supports_dataminer_collection=self.dataminer_collection)
        versions_structure_infos = [(version, self.dataminer_collection.get_structure_info(version)) for version in versions]
        structure_environment = StructureEnvironment(EnvironmentType.comparing, domain)
        between_versions = self._get_versions_between(all_versions, versions)

        comparison_environment = ComparisonEnvironment(structure_environment, versions_structure_infos, between_versions)
        data_files:tuple[tuple[int, Any], ...] = tuple((branch, self.structure.get_containerized_from_raw(self.dataminer_collection.get_data_file(version), version, comparison_environment[branch])) for branch, version in enumerate(versions))

        trace = Trace()
        comparison, _, _ = self.structure.compare(data_files, trace, comparison_environment)
        comparison = self.ensure_not_ellipsis(comparison, trace, versions, domain)
        if self.structure.delegate is None:
            output = self.ensure_not_ellipsis(self.structure.print_comparison(comparison, tuple(range(len(comparison_environment))), trace, comparison_environment), trace, versions, domain)
        else:
            output = self.ensure_not_ellipsis(self.structure.delegate.print_comparison(comparison, tuple(range(len(comparison_environment))), trace, comparison_environment), trace, versions, domain)
        with open(self.path, "wt", encoding="UTF8") as f:
            f.write(output)
