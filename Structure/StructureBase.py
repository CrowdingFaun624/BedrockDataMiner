from typing import TYPE_CHECKING, Any, TypeVar, Union

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.FileManager as FileManager

if TYPE_CHECKING:
    import Version.Version as Version

a = TypeVar("a")
b = TypeVar("b")
c = TypeVar("c", object, D.Diff)
d = TypeVar("d", object, D.Diff)

file_counts:dict[str,int] = {}

class StructureBase():
    '''Can be created by a DataMinerCollection to compare the output of the DataMiners with each other.'''

    def __init__(
            self,
            component_name:str,
            structure_name:str,
            children_tags:set[str],
        ) -> None:

        self.component_name = component_name
        self.structure_name = structure_name
        self.children_tags = children_tags

        self.structure:Structure.Structure|None = None
        self.normalizer:list[Normalizer.Normalizer]|None = None
        self.post_normalizer:list[Normalizer.Normalizer]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure,
        normalizer:list[Normalizer.Normalizer],
        post_normalizer:list[Normalizer.Normalizer],
    ) -> None:
        self.structure = structure
        self.normalizer = normalizer
        self.post_normalizer = post_normalizer

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.structure_name)

    def normalize(self, data:Any, environment:StructureEnvironment.StructureEnvironment) -> Any:
        '''
        Manipulates the data before comparison.
        :data: The data to manipulate.
        :environment: The StructureEnvironment to use.
        '''
        # base normalizer
        exceptions:list[Trace.ErrorTrace] = []
        if self.normalizer is None:
            raise Exceptions.AttributeNoneError("normalizer", self)
        output = data
        for normalizer_index, normalizer in enumerate(self.normalizer):
            try:
                output = normalizer(output)
            except Exception as e:
                output = None
                exceptions.append(Trace.ErrorTrace(e, self.component_name, normalizer_index, data))
                break
            else:
                if output is None:
                    exceptions.append(Trace.ErrorTrace(Exceptions.NormalizerNoneError(normalizer, self, "(index %i)" % (normalizer_index,)), self.component_name, normalizer_index, data))
                    break

        # other normalizers
        self.print_exception_list(exceptions)
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        normalizer_output, new_exceptions = self.structure.normalize(output, environment)
        exceptions.extend(new_exceptions)
        if normalizer_output is not None:
            output = normalizer_output

        if self.post_normalizer is None:
            raise Exceptions.AttributeNoneError("post_normalizer", self)
        for normalizer_index, normalizer in enumerate(self.post_normalizer):
            try:
                output = normalizer(output)
            except Exception as e:
                output = None
                exceptions.append(Trace.ErrorTrace(e, self.component_name, normalizer_index, data))
                break
            else:
                if output is None:
                    exceptions.append(Trace.ErrorTrace(Exceptions.NormalizerNoneError(normalizer, self, "(index %i)" % (normalizer_index,)), self.component_name, normalizer_index, data))
                    break

        self.print_exception_list(exceptions)
        return output

    def clear_caches(self) -> None:
        '''Clears all the caches of this Structure and of its children.'''
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        self.structure.clear_caches(set())

    def has_tag(self, tag:str) -> bool:
        '''
        Returns if the tag can be found in the Structure.
        :tag: The name of the tag.
        '''
        return tag in self.children_tags

    def get_tag_paths(self, data:Any, tag:str, environment:StructureEnvironment.StructureEnvironment) -> list[DataPath.DataPath]:
        '''
        Returns the DataPaths on which the given tag exists in the Structure for the given data.
        :data: The data to get the tag paths from.
        :tag: The tag to search for.
        :environment: The StructureEnvironment to use.
        '''
        if not self.has_tag(tag):
            return []
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        normalized_data = self.normalize(data, environment)
        output, new_exceptions = self.structure.get_tag_paths(normalized_data, tag, DataPath.DataPath([], self.component_name), environment)
        self.print_exception_list(new_exceptions)
        return output

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
        comparison_path = FileManager.get_comparison_file_path(name, store_number)
        if not comparison_path.parent.exists(): # type: ignore # >:(
            comparison_path.parent.mkdir() # type: ignore
        file_counts[name] = store_number
        with open(comparison_path, "wt", encoding="UTF8") as f:
            f.write(report)

    def comparison_report(
            self,
            data1:b,
            data2:b,
            version1:Union["Version.Version",None],
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
        header:list[str] = []
        beta_texts:list[str] = ["", ""]
        for index, version in enumerate((version1, version2)):
            if version is not None and version.get_order_tag().is_development_tag and version.parent is not None:
                beta_texts[index] = " (%s of \"%s\")" % (version.get_order_tag().development_name, version.parent.name)
        if version1 is None:
            header.append("Addition of \"%s\"%s at \"%s\"%s." % (self.structure_name, beta_texts[0], version2.name, beta_texts[1]))
        else:
            header.append("Difference of \"%s\" between \"%s\"%s and \"%s\"%s." % (self.structure_name, version1.name, beta_texts[0], version2.name, beta_texts[1]))
        if len(versions_between) > 0:
            files_word = "file" if len(versions_between) == 1 else "files"
            between_word = "before" if version1 is None else "between"
            if len(versions_between) > 10:
                header.append("Unable to create data %s for %i files %s." % (files_word, len(versions_between), between_word))
            elif len(versions_between) <= 10:
                header.append("Unable to create data files for %i %s %s: %s" % (len(versions_between), files_word, between_word, ", ".join("\"%s\"" % version.name for version in versions_between)))
        header.append("")

        if version1 is None:
            normalized_data2 = self.normalize(data2, environment)
            normalized_data1 = type(normalized_data2)() # create new empty.
        else:
            normalized_data1 = self.normalize(data1, environment)
            normalized_data2 = self.normalize(data2, environment)

        comparison_environment = StructureEnvironment.ComparisonEnvironment(environment, self.default_delegate, version1, version2, versions_between)
        data_comparison, has_changes = self.compare(normalized_data1, normalized_data2, environment)
        if not has_changes: # skip compare_text part
            return "", False

        lines, any_changes = self.compare_text(data_comparison, environment)

        final = header
        final.extend(str(line) for line in lines)

        return "\n".join(final), any_changes

    def check_types(self, data:Any, environment:StructureEnvironment.StructureEnvironment) -> None:
        '''
        Raises an exception with data about what went wrong if an error occurs.
        :data: The data to check.
        :environment: The StructureEnvironment to use.
        '''
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        traces = self.structure.check_all_types(data, environment)
        self.print_exception_list(traces)

    def print_exception_list(self, traces:list[Trace.ErrorTrace]) -> None:
        '''
        Prints all exceptions and traces in list and raises an exception at the end if the list has any items.
        :traces: The ErrorTraces to print.
        '''
        for trace in traces:
            print(trace.add(self.structure_name, None, force=True).finalize().stringify(), end="\n\n")
        if len(traces) > 0:
            raise Exceptions.StructureError(self)

    def compare(self, data1:Any, data2:Any, environment:StructureEnvironment.ComparisonEnvironment) -> tuple[Any,bool]:
        '''
        Combines the data into a single object with Diffs in it. Returns the combined object and if there are any differences.
        :data1: The data from the oldest Version.
        :data2: The data from the newest Version.
        :environment: The StructureEnvironment to use.
        '''
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        output, has_changes, traces = self.structure.compare(data1, data2, environment)
        self.print_exception_list(traces)
        return output, has_changes

    def compare_text(self, data:Any, environment:StructureEnvironment.ComparisonEnvironment) -> tuple[str,bool]:
        '''
        Generates Lines from an object containing Diffs.
        Returns a list of Lines and if there were any changes.
        :data: The object containing Diffs.
        :environment: The StructureEnvironment to use.
        '''
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        output, has_changes, traces = self.structure.compare_text(data, environment)
        self.print_exception_list(traces)
        return output, has_changes

    def print_text(self, data:Any, environment:StructureEnvironment.ComparisonEnvironment) -> str:
        '''
        Generates Lines from an object containing no Diffs.
        :data: The object containing no Diffs.
        :environment: The StructureEnvironment to use.
        '''
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        output, traces = self.structure.print_text(data, environment)
        self.print_exception_list(traces)
        return output
