import traceback
from typing import Any, TypeVar, TYPE_CHECKING, Union

import Structure.Structure as Structure
import Structure.StructureUtilities as SU
import Structure.Difference as D
import Structure.Normalizer as Normalizer
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
        TypeVerifier.TypedDictKeyTypeVerifier("name", "a str", True, str),
        TypeVerifier.TypedDictKeyTypeVerifier("normalizer", "a Normalizer or None", True, (Normalizer.Normalizer, type(None))),
        TypeVerifier.TypedDictKeyTypeVerifier("post_normalizer", "a Normalizer or None", True, (Normalizer.Normalizer, type(None))),
    )

    def __init__(
            self,
            name:str,
            normalizer:Normalizer.Normalizer|None,
            structure:Structure.Structure[b]|None,
            post_normalizer:Normalizer.Normalizer|None=None,
        ) -> None:
        self.type_verifier.base_verify({"name": name, "normalizer": normalizer, "structure": structure, "post_normalizer": post_normalizer})

        self.name = name
        self.normalizer = normalizer
        self.post_normalizer = post_normalizer
        self.structure = structure

    def normalize(self, data:Any, normalizer_dependencies:Normalizer.LocalNormalizerDependencies, version_number:int=1) -> Any:
        '''Manipulates the data before comparison.'''
        # base normalizer
        if self.normalizer is None:
            output = data
        else:
            output = self.normalizer(data, normalizer_dependencies, Trace.Trace(), version_number)
            if output is None:
                raise RuntimeError("Normalizer for \"%s\" returned None!" % (self.name))

        # other normalizers
        assert self.structure is not None
        self.structure.normalize(output, normalizer_dependencies, version_number, Trace.Trace())

        return output

    def store(self, report:str) -> None:
        if self.name is None:
            raise RuntimeError("Attempted to store StructureBase with uninitialized `name`!")
        if self.name in file_counts:
            store_number = file_counts[self.name] + 1
        else:
            store_number = 0
        comparison_path = FileManager.get_comparison_file_path(self.name, store_number)
        if not comparison_path.parent.exists(): # type: ignore # >:(
            comparison_path.parent.mkdir() # type: ignore
        file_counts[self.name] = store_number
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
        if self.name is None:
            raise RuntimeError("Attempted to create comparison report using StructureBase with uninitialized `name`!")
        header:list[str] = []
        beta_texts:list[str] = ["", ""]
        for index, version in enumerate((version1, version2)):
            if version is not None and version.ordering_tag is VersionTags.VersionTag.beta and version.parent is not None:
                beta_texts[index] = " (beta of \"%s\")" % version.parent.name
        if version1 is None:
            header.append("Addition of \"%s\"%s at \"%s\"%s." % (self.name, beta_texts[0], version2.name, beta_texts[1]))
        else:
            header.append("Difference of \"%s\" between \"%s\"%s and \"%s\"%s." % (self.name, version1.name, beta_texts[0], version2.name, beta_texts[1]))
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
        traces = self.structure.check_all_types(data, Trace.Trace())
        self.print_exception_list(traces)

    def print_exception_list(self, traces:list[tuple[Trace.Trace,Exception]]) -> None:
        '''Prints all exceptions and traces in list and raises an exception at the end if the list has any items.'''
        for trace, exception in traces:
            print("Exception in %s:" % trace)
            traceback.print_exception(exception)
            # raise exception
            print()
        if len(traces) > 0:
            raise TypeError("Type checking on %s failed!" % (self.name))

    def compare(self, data1:Any, data2:Any) -> Any:
        if self.structure is None:
            raise RuntimeError("`structure` was never initialized!")
        output, traces = self.structure.compare(data1, data2, Trace.Trace())
        self.print_exception_list(traces)
        return output

    def compare_text(self, data:Any) -> tuple[list[SU.Line],bool]:
        '''Returns a list of lines and if there were any changes'''
        if self.structure is None:
            raise RuntimeError("`structure` was never initialized!")
        return self.structure.compare_text(data, Trace.Trace())

    def print_text(self, data:Any) -> list[SU.Line]:
        if self.structure is None:
            raise RuntimeError("`structure` was never initialized!")
        return self.structure.print_text(data, Trace.Trace())
