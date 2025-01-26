from typing import TYPE_CHECKING, Any, Sequence

import Domain.Domain as Domain
import Structure.CacheStructure as CacheStructure
import Structure.DataPath as DataPath
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate
    import Version.Version as Version

file_counts:dict[str,int] = {}

class StructureBase():
    '''Can be created by a DataminerCollection to compare the output of the Dataminers with each other.'''

    __slots__ = (
        "cache_substructures",
        "children_has_garbage_collection",
        "children_tags",
        "default_delegate",
        "delegate",
        "domain",
        "name",
        "normalizer",
        "post_normalizer",
        "pre_normalized_types",
        "structure",
        "types",
    )

    def __init__(
            self,
            name:str,
            domain:"Domain.Domain",
            children_has_garbage_collection:bool,
        ) -> None:

        self.name = name
        self.domain = domain
        self.children_has_garbage_collection = children_has_garbage_collection

        self.structure:Structure.Structure
        self.types:tuple[type,...]
        self.pre_normalized_types:tuple[type,...]
        self.delegate:"Delegate.Delegate[str,StructureBase,str]|None"
        self.default_delegate:"Delegate.Delegate|None"
        self.normalizer:list[Normalizer.Normalizer]
        self.post_normalizer:list[Normalizer.Normalizer]
        self.cache_substructures:list[CacheStructure.CacheStructure] = []
        '''List of all descendants that are CacheStructures.'''
        self.children_tags:set[StructureTag.StructureTag]

    def link_substructures(
        self,
        structure:Structure.Structure,
        types:tuple[type,...],
        pre_normalized_types:tuple[type,...],
        delegate:"Delegate.Delegate|None",
        default_delegate:"Delegate.Delegate|None",
        normalizer:list[Normalizer.Normalizer],
        post_normalizer:list[Normalizer.Normalizer],
        children_tags:set[StructureTag.StructureTag],
    ) -> None:
        self.structure = structure
        self.types = types
        self.pre_normalized_types = pre_normalized_types
        self.delegate = delegate
        self.default_delegate = default_delegate
        self.normalizer = normalizer
        self.post_normalizer = post_normalizer
        self.children_tags = children_tags

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"

    def __hash__(self) -> int:
        return hash(self.name)

    def finalize(self) -> None:
        self.cache_substructures = [structure for structure in self.structure.get_descendants(set()) if isinstance(structure, CacheStructure.CacheStructure)]

    def normalize(self, data:Any, environment:StructureEnvironment.PrinterEnvironment) -> Any:
        '''
        Manipulates the data before comparison.
        :data: The data to manipulate.
        :environment: The PrinterEnvironment to use.
        '''
        version_tuple:tuple["Version.Version",...] = (environment.version,) if environment.version is not None else ()
        # base normalizer
        exceptions:list[Trace.ErrorTrace] = []
        if not isinstance(data, self.pre_normalized_types):
            exceptions.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"), self.name, None, data))
        self.print_exception_list(exceptions, version_tuple)
        output = data
        for normalizer_index, normalizer in enumerate(self.normalizer):
            if normalizer.version_range is not None and environment.get_version() not in normalizer.version_range: continue
            try:
                normalizer_output = normalizer(output)
            except Exception as e:
                output = None
                exceptions.append(Trace.ErrorTrace(e, self.name, normalizer_index, data))
                break
            else:
                if normalizer_output is not None:
                    output = normalizer_output
        self.print_exception_list(exceptions, version_tuple)

        # other normalizers
        normalizer_output, new_exceptions = self.structure.normalize(output, environment)
        exceptions.extend(new_exceptions)
        if normalizer_output is not None:
            output = normalizer_output
        self.print_exception_list(exceptions, version_tuple)

        for normalizer_index, normalizer in enumerate(self.post_normalizer):
            if normalizer.version_range is not None and environment.get_version() not in normalizer.version_range: continue
            try:
                normalizer_output = normalizer(output)
            except Exception as e:
                output = None
                exceptions.append(Trace.ErrorTrace(e, self.name, normalizer_index, data))
                break
            else:
                if normalizer_output is not None:
                    output = normalizer_output
        if not isinstance(output, self.types):
            exceptions.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.types, type(output), "Data"), self.name, None, output))
        self.print_exception_list(exceptions, version_tuple)

        return output

    def clear_caches(self) -> None:
        '''Clears all the caches of this Structure and of its children.'''
        for cache_structure in self.cache_substructures:
            cache_structure.clear_cache()

    def clear_some_caches(self) -> None:
        '''Clears items from caches of this Structure and all of its children that are too old.'''
        for cache_structure in self.cache_substructures:
            cache_structure.clear_old_items()

    def has_tag(self, tag:StructureTag.StructureTag) -> bool:
        '''
        Returns if the tag can be found in the Structure.
        :tag: The name of the tag.
        '''
        return tag in self.children_tags

    def has_tags(self, tags:list[StructureTag.StructureTag]) -> bool:
        '''
        Returns if any tag can be found in the Structure.
        :tags: The name of the tags.
        '''
        for tag in tags:
            if tag in self.children_tags:
                return True
        return False

    def get_tag_paths(self, data:Any, tags:list[StructureTag.StructureTag], environment:StructureEnvironment.PrinterEnvironment, *, normalized_data:Any|None=None) -> dict[StructureTag.StructureTag,Sequence[DataPath.DataPath]]:
        '''
        Returns the DataPaths on which the given tag exists in the Structure for the given data.
        :data: The data to get the tag paths from.
        :tag: The tag to search for.
        :environment: The PrinterEnvironment to use.
        '''
        if not self.has_tags(tags):
            # optimization: don't need to even normalize!
            return {tag: () for tag in tags}
        version_tuple:tuple["Version.Version",...] = (environment.version,) if environment.version is not None else ()
        output:dict[StructureTag.StructureTag,Sequence[DataPath.DataPath]] = {}
        if normalized_data is None:
            normalized_data = self.normalize(data, environment)
        for tag in tags:
            if not self.has_tag(tag):
                output[tag] = ()
            paths, new_exceptions = self.structure.get_tag_paths(normalized_data, tag, DataPath.DataPath([], self.name), environment.structure_environment)
            self.print_exception_list(new_exceptions, version_tuple)
            output[tag] = paths
        return output

    def get_referenced_files(self, data:Any, environment:StructureEnvironment.PrinterEnvironment, referenced_files:set[int], *, normalized_data:Any|None=None) -> None:
        '''
        Returns any Files within the data.
        :data: The data to search for Files.
        :environment: The PrinterEnvironment to use.
        '''
        if self.children_has_garbage_collection:
            normalized_data = self.normalize(data, environment) if normalized_data is None else normalized_data
            self.structure.get_referenced_files(normalized_data, environment, referenced_files)

    def store(self, report:str, name:str) -> None:
        '''
        Stores a comparison report.
        :report: The comparison report string.
        :name: The name of the folder to store the report in.
        '''
        if name in file_counts:
            store_number = file_counts[name] + 1
        else:
            store_number = 0
        comparison_path = self.domain.get_comparison_file_path(name, store_number)
        file_counts[name] = store_number
        with open(comparison_path, "wt", encoding="UTF8") as f:
            f.write(report)

    def comparison_report[b](
            self,
            data1:b,
            data2:b,
            version1:"Version.Version|None",
            version2:"Version.Version",
            versions_between:list["Version.Version"],
            environment:StructureEnvironment.StructureEnvironment,
        ) -> tuple[str,bool]:
        '''
        Returns a final string of the comparison report and a boolean if there were any changes.
        :data1: The data from the first Version.
        :data2: The data from the second Version.
        :version1: The oldest Version.
        :version2: The newest Version.
        :versions_between: A list of any Versions between the first and second Versions.
        :environment: The StructureEnvironment to use.
        '''
        comparison_environment = StructureEnvironment.ComparisonEnvironment(environment, self.default_delegate, [version1, version2], [versions_between], False)
        if version1 is None:
            normalized_data2 = self.normalize(data2, comparison_environment[1])
            if hasattr(normalized_data2, "__copy_empty__"):
                normalized_data1 = normalized_data2.__copy_empty__()
            else:
                normalized_data1 = type(normalized_data2)() # create new empty object.
        else:
            normalized_data1 = self.normalize(data1, comparison_environment[0])
            normalized_data2 = self.normalize(data2, comparison_environment[1])

        self.check_types(normalized_data1, environment, (version1,) if version1 is not None else ())
        self.check_types(normalized_data2, environment, (version2,))

        data_comparison, has_changes = self.compare(normalized_data1, normalized_data2, comparison_environment)
        if not has_changes: # skip compare_text part
            return "", False
        return self.compare_text(data_comparison, comparison_environment)

    def check_types(self, data:Any, environment:StructureEnvironment.StructureEnvironment, versions:tuple["Version.Version",...]) -> None:
        '''
        Raises an exception with data about what went wrong if an error occurs.
        :data: The data to check.
        :environment: The StructureEnvironment to use.
        '''
        traces = self.structure.check_all_types(data, environment)
        self.print_exception_list(traces, versions)

    def print_exception_list(self, traces:Sequence[Trace.ErrorTrace], versions:tuple["Version.Version",...]) -> None:
        '''
        Prints all exceptions and traces in list and raises an exception at the end if the list has any items.
        :traces: The ErrorTraces to print.
        '''
        texts:list[str] = []
        for trace in traces:
            text = trace.add(self.name, None, force=True).finalize().stringify() + "\n\n"
            print(text)
            texts.append(text)
        if len(traces) > 0:
            if (log := self.domain.logs.get("structure_log")) is not None and log.supports_type(log, str):
                log.write(f"-------- {len(traces)} EXCEPTIONS IN {self.name} ON {", ".join(version.name for version in versions)} --------\n\n")
                log.write("".join(texts))
            raise Exceptions.StructureError(self)

    def compare_many(self, *data:Any, environment:StructureEnvironment.ComparisonEnvironment) -> tuple[Any,bool]:
        '''
        Combines many data into a single object with Diffs in it. Returns the combined object and if there are any differences.
        :data: The normalized data in order from oldest to newest.
        :environment: The StructureEnvironment to use.
        '''
        output = data[0]
        has_changes = False
        for index, item in enumerate(data[1:]):
            # branch refers to the index of the newest part of the older data (output).
            output, any_changes, traces = self.structure.compare(output, item, environment, index, len(data))
            has_changes = has_changes or any_changes
            self.print_exception_list(traces, environment.get_non_none_versions())
        return output, has_changes

    def compare(self, data1:Any, data2:Any, environment:StructureEnvironment.ComparisonEnvironment) -> tuple[Any,bool]:
        '''
        Combines the data into a single object with Diffs in it. Returns the combined object and if there are any differences.
        :data1: The normalized data from the oldest Version.
        :data2: The normalized data from the newest Version.
        :environment: The StructureEnvironment to use.
        '''
        output, has_changes, traces = self.structure.compare(data1, data2, environment, 0, 2)
        self.print_exception_list(traces, environment.get_non_none_versions())
        return output, has_changes

    def compare_text(self, data:Any, environment:StructureEnvironment.ComparisonEnvironment) -> tuple[str,bool]:
        '''
        Generates Lines from an object containing Diffs.
        Returns a list of Lines and if there were any changes.
        :data: The object containing Diffs.
        :environment: The StructureEnvironment to use.
        '''
        if self.delegate is None:
            output, has_changes, traces = self.structure.compare_text(data, environment)
        else:
            output, has_changes, traces = self.delegate.compare_text(data, environment)
        self.print_exception_list(traces, environment.get_non_none_versions())
        return output, has_changes

    def print_text(self, data:Any, environment:StructureEnvironment.PrinterEnvironment) -> str:
        '''
        Generates Lines from an object containing no Diffs.
        :data: The object containing no Diffs.
        :environment: The StructureEnvironment to use.
        '''
        version_tuple:tuple["Version.Version",...] = (environment.version,) if environment.version is not None else ()
        if self.delegate is None:
            output, traces = self.structure.print_text(data, environment)
        else:
            output, traces = self.delegate.print_text(data, environment)
        self.print_exception_list(traces, version_tuple)
        return output
