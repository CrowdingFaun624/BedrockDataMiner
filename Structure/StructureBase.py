from typing import Any, TypeVar, TYPE_CHECKING, Union

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.FileManager as FileManager
import Utilities.TypeVerifier as TypeVerifier
import Utilities.VersionTags as VersionTags

if TYPE_CHECKING:
    import Utilities.Version as Version

a = TypeVar("a")
b = TypeVar("b")
c = TypeVar("c", object, D.Diff)
d = TypeVar("d", object, D.Diff)

file_counts:dict[str,int] = {}

class StructureBase():
    '''Can be created by a DataMinerCollection to compare the output of the DataMiners with each other.'''

    type_verifier = TypeVerifier.TypedDictTypeVerifier(
        TypeVerifier.TypedDictKeyTypeVerifier("structure", "a Structure or None", True, (Structure.Structure, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("component_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("structure_name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a Normalizer or None", True, (Normalizer.Normalizer, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a Normalizer or None", True, (Normalizer.Normalizer, type(None))),
    )

    def __init__(
            self,
            component_name:str,
            structure_name:str,
            normalizer:Normalizer.Normalizer|None,
            structure:Structure.Structure[b]|None,
            post_normalizer:Normalizer.Normalizer|None,
            children_tags:set[str],
        ) -> None:
        self.type_verifier.base_verify({"component_name": component_name, "structure_name": structure_name, "normalizer": normalizer, "structure": structure, "post_normalizer": post_normalizer})

        self.component_name = component_name
        self.structure_name = structure_name
        self.normalizer = normalizer
        self.post_normalizer = post_normalizer
        self.structure = structure
        self.children_tags = children_tags

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.structure_name)

    def normalize(self, data:Any, normalizer_dependencies:Normalizer.LocalNormalizerDependencies, version_number:int=1) -> Any:
        '''Manipulates the data before comparison.'''
        # base normalizer
        exceptions:list[Trace.ErrorTrace] = []
        if self.normalizer is None:
            output = data
        else:
            try:
                output = self.normalizer(data, normalizer_dependencies, version_number)
            except Exception as e:
                output = None
                exceptions.append(Trace.ErrorTrace(e, self.component_name, None, data))
            else:
                if output is None:
                    exceptions.append(Trace.ErrorTrace(RuntimeError("Output of normalizer is None!"), self.component_name, None, data))
                    output = None

        # other normalizers
        self.print_exception_list(exceptions)
        assert self.structure is not None
        normalizer_output, new_exceptions = self.structure.normalize(output, normalizer_dependencies, version_number)
        exceptions.extend(new_exceptions)
        if normalizer_output is not None:
            output = normalizer_output
        self.print_exception_list(exceptions)
        return output

    def has_tag(self, tag:str) -> bool:
        return tag in self.children_tags

    def get_tag_paths(self, data:Any, tag:str, version:"Version.Version", normalizer_dependencies:Normalizer.NormalizerDependencies) -> list[DataPath.DataPath]:
        if not self.has_tag(tag):
            return []
        assert self.structure is not None
        local_normalizer_dependencies = Normalizer.LocalNormalizerDependencies(normalizer_dependencies, version, None)
        normalized_data = self.normalize(data, local_normalizer_dependencies, 1)
        output, new_exceptions = self.structure.get_tag_paths(normalized_data, tag, DataPath.DataPath([], self.component_name))
        self.print_exception_list(new_exceptions)
        return output

    def store(self, report:str, name:str) -> None:
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
            normalizer_dependencies:Normalizer.NormalizerDependencies,
        ) -> tuple[str,bool]:
        '''Returns a final string of the comparison report and a boolean if there were any changes.'''
        header:list[str] = []
        beta_texts:list[str] = ["", ""]
        for index, version in enumerate((version1, version2)):
            if version is not None and version.ordering_tag is VersionTags.VersionTag.beta and version.parent is not None:
                beta_texts[index] = " (beta of \"%s\")" % version.parent.name
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

        local_normalizer_dependencies = Normalizer.LocalNormalizerDependencies(normalizer_dependencies, version1, version2)
        if version1 is None:
            normalized_data2 = self.normalize(data2, local_normalizer_dependencies, 2)
            normalized_data1 = type(normalized_data2)() # create new empty.
        else:
            normalized_data1 = self.normalize(data1, local_normalizer_dependencies, 1)
            normalized_data2 = self.normalize(data2, local_normalizer_dependencies, 2)

        data_comparison = self.compare(normalized_data1, normalized_data2)

        lines, any_changes = self.compare_text(data_comparison)

        final = header
        final.extend(str(line) for line in lines)

        return "\n".join(final), any_changes

    def check_types(self, data:Any) -> None:
        '''Raises an exception with data about what went wrong if an error occurs.'''
        if self.structure is None:
            raise RuntimeError("`structure` was never initialized!")
        traces = self.structure.check_all_types(data)
        self.print_exception_list(traces)

    def print_exception_list(self, traces:list[Trace.ErrorTrace]) -> None:
        '''Prints all exceptions and traces in list and raises an exception at the end if the list has any items.'''
        for trace in traces:
            trace.add(self.structure_name, None, force=True)
            trace.finalize()
            print(trace.stringify())
            print()
        if len(traces) > 0:
            raise TypeError("Type checking on %s failed!" % (self.structure_name))

    def compare(self, data1:Any, data2:Any) -> Any:
        if self.structure is None:
            raise RuntimeError("`structure` was never initialized!")
        output, traces = self.structure.compare(data1, data2)
        self.print_exception_list(traces)
        return output

    def compare_text(self, data:Any) -> tuple[list[SU.Line],bool]:
        '''Returns a list of lines and if there were any changes'''
        if self.structure is None:
            raise RuntimeError("`structure` was never initialized!")
        output, has_changes, traces = self.structure.compare_text(data)
        self.print_exception_list(traces)
        return output, has_changes

    def print_text(self, data:Any) -> list[SU.Line]:
        if self.structure is None:
            raise RuntimeError("`structure` was never initialized!")
        output, traces = self.structure.print_text(data)
        self.print_exception_list(traces)
        return output
