from types import EllipsisType
from typing import Any, Container, Self, Sequence, cast

from Structure.BranchlessStructure import BranchlessStructure
from Structure.Container import Con, Don
from Structure.DataPath import DataPath
from Structure.Delegate.Delegate import Delegate, DelegateCreator
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
from Utilities.Log import Log
from Utilities.Trace import Trace
from Version.Version import Version


class StructureBase[D, BO, CO](BranchlessStructure[D, BO, CO]):

    __slots__ = (
        "_cache_substructures",
        "delegate",
        "delegate_creator",
        "log",
    )

    def link_structure_base(
        self,
        delegate:DelegateCreator[Delegate[Con[D], Don[D]|Diff[Don[D]], Self, str, Any, str, Any]]|None,
        log:Log|None
    ) -> None:
        self.trace_name = self.full_name
        self.delegate_creator = delegate
        self.log = log
        self._cache_substructures:Sequence[CacheStructure]|None = None

    def finalize_structure_base(self, trace:Trace) -> bool:
        self.delegate = None if self.delegate_creator is None else self.delegate_creator.create_delegate(self)
        del self.delegate_creator
        return False if self.delegate is None else self.delegate.finalize(self.domain, trace)

    @property
    def cache_substructures(self) -> Sequence[CacheStructure]:
        if self._cache_substructures is None:
            self._cache_substructures = [structure for structure in self.get_descendants(set()) if isinstance(structure, CacheStructure)]
        return self._cache_substructures

    def clear_old_caches(self, structure_infos:Container[tuple[Version, StructureInfo]]) -> None:
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

    def print_exception_list(self, trace:Trace, versions:Sequence["Version"], raise_exception:bool=False) -> bool:
        """
        Prints all exceptions and traces in list and raises an exception at the end if the list has any items.
        """
        texts:list[str] = list(trace.stringify())
        if trace.has_exceptions:
            if self.log is not None and self.log.supports_type(self.log, str):
                self.log.write(f"-------- {trace.exception_count} EXCEPTIONS IN {self.full_name} ON {", ".join(version.name for version in versions)} --------\n\n")
                self.log.write("\n".join(texts))
            for text in texts:
                print(text)
            if raise_exception:
                raise StructureError(self)
        return len(trace._exceptions) > 0

    def ensure_not_ellipsis[a](self, data:a|EllipsisType, trace:Trace, versions:Sequence["Version"]) -> a:
        if self.print_exception_list(trace, versions) or data is ...:
            raise StructureError(self)
        else:
            return data

    def store(self, report:str, name:str) -> None:
        """
        Stores a comparison report.

        :param report: The comparison report string.
        :param name: The name of the folder to store the report in.
        """
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
        """
        Returns a final string of the initial report at the first Version that supports this StructureBase.

        :param data: The data from `version`.
        """
        printer_environment = PrinterEnvironment(environment, structure_info, version, 0)
        trace = Trace()
        containerized_data = self.ensure_not_ellipsis(self.containerize(data, trace, printer_environment), trace, (version,))
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
        comparison_environment = ComparisonEnvironment(environment, [(version1, structure_info1), (version2, structure_info2)], [versions_between])
        trace = Trace()
        containerized_data1 = self.ensure_not_ellipsis(self.containerize(data1, trace, comparison_environment[0]), trace, (version1,))
        containerized_data2 = self.ensure_not_ellipsis(self.containerize(data2, trace, comparison_environment[1]), trace, (version2,))
        self.ensure_not_ellipsis(self.type_check(containerized_data1, trace, comparison_environment[0]), trace, (version1,))
        self.ensure_not_ellipsis(self.type_check(containerized_data2, trace, comparison_environment[1]), trace, (version2,))
        comparison, has_changes, _ = self.compare(((0, containerized_data1), (1, containerized_data2)), trace, comparison_environment)
        comparison = self.ensure_not_ellipsis(comparison, trace, (version1, version2))
        if not has_changes:
            return "", False
        if self.delegate is None:
            return cast(str, self.ensure_not_ellipsis(self.print_comparison(comparison, (0, 1), trace, comparison_environment), trace, (version1, version2))), has_changes
        else:
            output = ...
            with trace.enter(self, self.trace_name, (containerized_data1, containerized_data2)):
                output = self.delegate.print_comparison(comparison, (0, 1), trace, comparison_environment)
            return self.ensure_not_ellipsis(output, trace, (version1, version2)), has_changes

    def get_containerized_from_raw(self, data:D, version:Version, environment:PrinterEnvironment) -> Con[D]:
        trace = Trace()
        return self.ensure_not_ellipsis(self.containerize(data, trace, environment), trace, (version,))

    def type_check_from_raw(self, data:D, version:Version, environment:PrinterEnvironment) -> None:
        trace = Trace()
        containerized_data = self.get_containerized_from_raw(data, version, environment)
        self.type_check(containerized_data, trace, environment)
        self.print_exception_list(trace, (version,), raise_exception=True)

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
