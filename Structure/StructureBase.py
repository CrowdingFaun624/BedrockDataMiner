from types import EllipsisType
from typing import Any, Container, Self, Sequence, cast

import Domain.Domain as Domain
from Structure.BranchlessStructure import BranchlessStructure
from Structure.Container import Con, Don
from Structure.DataPath import DataPath
from Structure.Delegate.Delegate import Delegate
from Structure.Difference import Diff
from Structure.StructureEnvironment import (
    ComparisonEnvironment,
    PrinterEnvironment,
    StructureEnvironment,
)
from Structure.StructureInfo import StructureInfo
from Structure.StructureTag import StructureTag
from Structure.StructureTypes.CacheStructure import CacheStructure
from Utilities.Exceptions import StructureError
from Utilities.Trace import Trace
from Version.Version import Version


class StructureBase[D, BO, CO](BranchlessStructure[D, BO, CO]):

    __slots__ = (
        "cache_substructures",
        "delegate",
        "default_delegate",
        "domain",
    )

    def link_structure_base(
        self,
        default_delegate:Delegate|None,
        delegate:Delegate[Con[D], Don[D]|Diff[Don[D]], Self, str, Any, str, Any]|None,
        domain:"Domain.Domain",
    ) -> None:
        self.default_delegate = default_delegate
        self.delegate = delegate
        self.domain = domain

    def finalize(self) -> None:
        self.cache_substructures = [structure for structure in self.get_descendants(set()) if isinstance(structure, CacheStructure)]

    def clear_old_caches(self, structure_infos:Container[StructureInfo]) -> None:
        for cache_structure in self.cache_substructures:
            cache_structure.clear_old()
        for structure in self.get_descendants(set()):
            structure.clear_similarity_cache(structure_infos)

    def clear_all_caches(self) -> None:
        for cache_structure in self.cache_substructures:
            cache_structure.clear_all()
        for structure in self.get_descendants(set()):
            structure.clear_similarity_cache(())

    def has_tag(self, tag:StructureTag) -> bool:
        return tag in self.children_tags

    def has_tags(self, tags:list[StructureTag]) -> bool:
        return any(self.has_tag(tag) for tag in tags)

    def print_exception_list(self, trace:Trace, versions:Sequence["Version"]) -> bool:
        '''
        Prints all exceptions and traces in list and raises an exception at the end if the list has any items.
        '''
        texts:list[str] = list(trace.stringify())
        if trace.has_exceptions > 0:
            if (log := self.domain.logs.get("structure_log")) is not None and log.supports_type(log, str):
                log.write(f"-------- {trace.exception_count} EXCEPTIONS IN {self.full_name} ON {", ".join(version.name for version in versions)} --------\n\n")
                log.write("\n".join(texts))
            for text in texts:
                print(text)
        return len(trace._exceptions) > 0

    def ensure_not_ellipsis[a](self, data:a|EllipsisType, trace:Trace, versions:Sequence["Version"]) -> a:
        if self.print_exception_list(trace, versions) or data is ...:
            raise StructureError(self)
        else:
            return data

    def store(self, report:str, name:str) -> None:
        '''
        Stores a comparison report.
        :report: The comparison report string.
        :name: The name of the folder to store the report in.
        '''
        file_counts = self.domain.comparison_file_counts
        if name in file_counts:
            store_number = file_counts[name] + 1
        else:
            store_number = 0
        comparison_path = self.domain.get_comparison_file_path(name, store_number)
        file_counts[name] = store_number
        with open(comparison_path, "wt", encoding="UTF8") as f:
            f.write(report)

    def initial_report(self, data:D, version:Version, structure_info:StructureInfo, environment:StructureEnvironment) -> str:
        '''
        Returns a final string of the initial report at the first Version that supports this StructureBase.
        :data: The un-normalized data from `version`.
        '''
        printer_environment = PrinterEnvironment(environment, structure_info, self.default_delegate, version, 0)
        trace = Trace()
        normalized_data = self.ensure_not_ellipsis(self.normalize_from_raw(data, trace, printer_environment), trace, (version,))
        containerized_data = self.ensure_not_ellipsis(self.containerize(normalized_data, trace, printer_environment), trace, (version,))
        self.ensure_not_ellipsis(self.type_check(containerized_data, trace, printer_environment), trace, (version,))
        if self.delegate is None:
            return cast(str, self.ensure_not_ellipsis(self.print_branch(containerized_data, trace, printer_environment), trace, (version,)))
        else:
            return self.ensure_not_ellipsis(self.delegate.print_branch(containerized_data, trace, printer_environment), trace, (version,))

    def comparison_report_two(
        self,
        data1:D,
        data2:D,
        version1:Version,
        version2:Version,
        structure_info1:StructureInfo,
        structure_info2:StructureInfo,
        versions_between:list[Version],
        environment:StructureEnvironment,
    ) -> tuple[str, bool]:
        comparison_environment = ComparisonEnvironment(environment, self.default_delegate, [(version1, structure_info1), (version2, structure_info2)], [versions_between])
        trace = Trace()
        normalized_data1 = self.ensure_not_ellipsis(self.normalize_from_raw(data1, trace, comparison_environment[0]), trace, (version1,))
        normalized_data2 = self.ensure_not_ellipsis(self.normalize_from_raw(data2, trace, comparison_environment[1]), trace, (version2,))
        containerized_data1 = self.ensure_not_ellipsis(self.containerize(normalized_data1, trace, comparison_environment[0]), trace, (version1,))
        containerized_data2 = self.ensure_not_ellipsis(self.containerize(normalized_data2, trace, comparison_environment[1]), trace, (version2,))
        self.ensure_not_ellipsis(self.type_check(containerized_data1, trace, comparison_environment[0]), trace, (version1,))
        self.ensure_not_ellipsis(self.type_check(containerized_data2, trace, comparison_environment[1]), trace, (version2,))
        comparison, has_changes, _ = self.compare(((0, containerized_data1), (1, containerized_data2)), trace, comparison_environment)
        if not has_changes:
            return "", False
        comparison = self.ensure_not_ellipsis(comparison, trace, (version1, version2))
        if self.delegate is None:
            return cast(str, self.ensure_not_ellipsis(self.print_comparison(comparison, (0, 1), trace, comparison_environment), trace, (version1, version2))), has_changes
        else:
            with trace.enter(self, self.name, (containerized_data1, containerized_data2)):
                return self.ensure_not_ellipsis(self.delegate.print_comparison(comparison, (0, 1), trace, comparison_environment), trace, (version1, version2)), has_changes
            return "", False

    def normalize_from_raw(self, data:D, trace:Trace, environment:PrinterEnvironment) -> D:
        output = self.normalize(data, trace, environment)
        return data if output is ... else output

    def get_containerized_from_raw(self, data:D, version:Version, environment:PrinterEnvironment) -> Con[D]:
        trace = Trace()
        normalized_data = self.ensure_not_ellipsis(self.normalize_from_raw(data, trace, environment), trace, (version,))
        return self.ensure_not_ellipsis(self.containerize(normalized_data, trace, environment), trace, (version,))

    def type_check_from_raw(self, data:D, version:Version, environment:PrinterEnvironment) -> None:
        trace = Trace()
        containerized_data = self.get_containerized_from_raw(data, version, environment)
        self.type_check(containerized_data, trace, environment)
        self.print_exception_list(trace, (version,))

    def get_tag_paths_from_raw(
        self,
        data:D,
        tags:list[StructureTag],
        version:Version,
        environment:PrinterEnvironment,
    ) -> dict[StructureTag,Sequence[DataPath]]:
        containerized_data = self.get_containerized_from_raw(data, version, environment)
        return self.get_tag_paths_from_containerized(containerized_data, tags, version, environment)

    def get_tag_paths_from_containerized(
        self,
        containerized_data:Con[D],
        tags:list[StructureTag],
        version:Version,
        environment:PrinterEnvironment,
    )-> dict[StructureTag,Sequence[DataPath]]:
        trace = Trace()
        return {tag: self.ensure_not_ellipsis(self.get_tag_paths(containerized_data, tag, DataPath([], self.name), trace, environment), trace, (version,)) for tag in tags}
