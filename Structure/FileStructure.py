from typing import (TYPE_CHECKING, Any, Callable, Iterable, Iterator, Union,
                    cast)

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.ObjectStructure as ObjectStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.File as File

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate

class FileStructure[a](ObjectStructure.ObjectStructure[File.AbstractFile[a]]):

    def __init__(
        self,
        name: str,
        max_similarity_descendent_depth:int|None,
        max_similarity_ancestor_depth:int|None,
        children_has_normalizer: bool,
        children_has_garbage_collection:bool,
    ) -> None:
        super().__init__(name, children_has_normalizer, children_has_garbage_collection)

        self.max_similarity_descendent_depth = max_similarity_descendent_depth
        self.max_similarity_ancestor_depth = max_similarity_ancestor_depth

        self.structure:Structure.Structure[a]|None = None
        self.delegate:Union["Delegate.Delegate", None] = None
        self.file_types:tuple[type,...]|None = None
        self.content_types:tuple[type,...]|None = None
        self.normalizer:list[Normalizer.Normalizer]|None = None
        self.post_normalizer:list[Normalizer.Normalizer]|None = None
        self.pre_normalized_types:tuple[type,...]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure[a]|None,
        delegate:Union["Delegate.Delegate", None],
        file_types:tuple[type,...],
        content_types:tuple[type,...],
        normalizer:list[Normalizer.Normalizer],
        post_normalizer:list[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
        children_tags:set[StructureTag.StructureTag],
    ) -> None:
        super().link_substructures(delegate, children_tags)
        self.structure = structure
        self.file_types = file_types
        self.content_types = content_types
        self.normalizer = normalizer
        self.post_normalizer = post_normalizer
        self.pre_normalized_types = pre_normalized_types

    def get_structure(self, key:None, value:a) -> tuple[Structure.Structure[a]|None, list[Trace.ErrorTrace]]:
        return self.structure, []

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.structure is None: return []
        else: return [self.structure]

    def check_all_types(self, data:File.AbstractFile[a], environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        output:list[Trace.ErrorTrace] = []
        if self.file_types is None:
            raise Exceptions.AttributeNoneError("file_types", self)
        if self.content_types is None:
            raise Exceptions.AttributeNoneError("content_types", self)
        if not isinstance(data, self.file_types):
            output.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.file_types, type(data), "Data", "(file)"), self.name, None, data))
            return output
        if not isinstance(data.data, self.content_types):
            output.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.content_types, type(data.data), "Data", "(content)"), self.name, None, data.data))
        if self.structure is not None:
            output.extend(exception.add(self.name, None) for exception in self.structure.check_all_types(data.data, environment))
        return output

    def normalize(self, data:File.AbstractFile[a], environment:StructureEnvironment.PrinterEnvironment) -> tuple[Any|None, list[Trace.ErrorTrace]]:
        if not self.children_has_normalizer: return None, []
        if self.normalizer is None:
            raise Exceptions.AttributeNoneError("normalizer", self)
        if self.post_normalizer is None:
            raise Exceptions.AttributeNoneError("post_normalizer", self)
        if self.pre_normalized_types is None:
            raise Exceptions.AttributeNoneError("pre_normalized_types", self)
        if self.file_types is None:
            raise Exceptions.AttributeNoneError("file_types", self)
        exceptions:list[Trace.ErrorTrace] = []
        if not isinstance(data, self.pre_normalized_types):
            exceptions.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"), self.name, None, data))
            return None, exceptions

        data_identity_changed = False
        for normalizer in self.normalizer:
            if normalizer.version_range is not None and environment.get_version() not in normalizer.version_range: continue
            try:
                if isinstance(data, File.File):
                    normalizer_output = normalizer(data.data)
                    if normalizer_output is not None:
                        data.data = normalizer_output
                        # no need to change `data_identity_changed`
                else:
                    normalizer_output = normalizer(data)
                    if normalizer_output is not None:
                        data_identity_changed = True
                        data = normalizer_output
            except Exception as e:
                exceptions.append(Trace.ErrorTrace(e, self.name, None, data))
        
        if not isinstance(data, self.file_types): # quite often are there bugs that cause data not to be a file.
            exceptions.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.file_types, type(data), "Data"), self.name, None, data))
            return None, exceptions

        if self.structure is not None:
            normalizer_output, new_exceptions = self.structure.normalize(data.data, environment)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
            if normalizer_output is not None:
                data_identity_changed = True
                data.data = normalizer_output

        for normalizer in self.post_normalizer:
            if normalizer.version_range is not None and environment.get_version() not in normalizer.version_range: continue
            try:
                normalizer_output = normalizer(data.data)
                if normalizer_output is not None:
                    data_identity_changed = True
                    data.data = normalizer_output
            except Exception as e:
                exceptions.append(Trace.ErrorTrace(e, self.name, None, data))
                return None, exceptions

        if data_identity_changed:
            return data, exceptions
        else:
            return None, exceptions

    def get_tag_paths(self, data:File.AbstractFile[a], tag: StructureTag.StructureTag, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        if self.children_tags is None:
            raise Exceptions.AttributeNoneError("children_tags", self)
        if tag not in self.children_tags: return [], []
        exceptions:list[Trace.ErrorTrace] = []
        if self.structure is None:
            return [], exceptions
        output, new_exceptions = self.structure.get_tag_paths(data.data, tag, data_path.copy(), environment)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, exceptions

    def get_referenced_files(self, data: File.AbstractFile[a], environment: StructureEnvironment.PrinterEnvironment) -> Iterator[int]:
        if self.children_has_garbage_collection:
            yield data.hash
        if self.structure is not None and self.structure.children_has_garbage_collection:
            # getting if its child has a file because self.children_has_garbage_collection is
            # always true for FileStructure objects, but if we do cancel this
            # function it's a big deal because getting file data is expensive.
            yield from self.structure.get_referenced_files(data.data, environment)

    def get_similarity(self, data1: File.AbstractFile[a]|File.FileDiff[a], data2: File.AbstractFile[a], depth:int, max_depth:int|None, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace], branch:int) -> float:
        if (max_depth is not None and depth > max_depth) or (self.max_similarity_ancestor_depth is not None and depth > self.max_similarity_ancestor_depth) or self.structure is None:
            if branch == 0:
                return float(data1 == data2)
            else:
                return float(Structure.get_data_at_branch(data1, branch) == data2)
        else:
            data1_data = data1.last_value.data if isinstance(data1, File.FileDiff) else data1.data
            output = self.structure.get_similarity(data1_data, data2.data, depth + 1, max_depth, environment, exceptions, branch)
            return output

    def compare(self, data1:File.AbstractFile[a]|File.FileDiff[a], data2:File.AbstractFile[a], environment:StructureEnvironment.ComparisonEnvironment, branch:int, branches:int) -> tuple[File.FileDiff[a], bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        if not isinstance(data1, File.FileDiff) and (data1 is data2 or data1 == data2):
            output, has_changes = File.FileDiff(data1.data, data1, data2), False
        elif self.structure is None:
            has_changes = True
            if isinstance(data1, File.FileDiff):
                if isinstance(data1.data, D.Diff):
                    data1_data = cast("D.Diff[a]", data1.data)
                    if data1.last_value == data2:
                        output_diff = data1_data.extend(branch+1)
                    else:
                        output_diff = data1_data.append(branch+1, data2.data)
                else:
                    # data1 has had no changes across all previous comparisons. self has no Structure, so changes always result in Diffs.
                    if data1.last_value == data2:
                        output_diff = data1.last_value.data
                    else:
                        output_diff = D.Diff(branches, {tuple(range(0,branch+1)): data1.data, (branch+1,): data2.data})
                new_files = list(data1.files)
                new_files.append(data2)
                output = File.FileDiff(output_diff, *new_files)
            else:
                output = File.FileDiff(D.Diff(branches, {tuple(range(0,branch+1)): data1.data, (branch+1,): data2.data}), data1, data2)
        else:
            comparison_output, has_changes, new_exceptions = self.structure.compare(D.last_value(data1.data), data2.data, environment, branch, branches)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
            if isinstance(data1, File.FileDiff):
                new_files = list(data1.files)
                new_files.append(data2)
            else:
                new_files = [data1, data2]
            if isinstance(data1.data, D.Diff):
                data1_data = cast("D.Diff[a]", data1.data)
                output = File.FileDiff(data1_data.with_last_as(branch+1, comparison_output), *new_files)
            else:
                output = File.FileDiff(comparison_output, *new_files)
        return output, has_changes, exceptions

    def print_text(self, data: File.AbstractFile[a], environment:StructureEnvironment.PrinterEnvironment) -> tuple[Any, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.get_structure(None, data.data)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        if self.delegate is not None:
            printer = self.delegate
        elif structure is not None:
            printer = structure
        elif environment.default_delegate is not None:
            printer = environment.default_delegate
        else:
            raise Exceptions.AttributeNoneError("delegate", self)
        output, new_exceptions = printer.print_text(data.data, environment)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, exceptions

    def compare_text(self, data:File.FileDiff[a], environment:StructureEnvironment.ComparisonEnvironment) -> tuple[Any, bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        data_extracted = data.data
        structure, new_exceptions = self.choose_structure(None, data_extracted)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        comparer:Callable[[Any, StructureEnvironment.ComparisonEnvironment],tuple[Any,bool,list[Trace.ErrorTrace]]]
        if self.delegate is not None:
            comparer = self.delegate.compare_text
        elif structure is not None and None in structure and structure[None] is not None:
            comparer = lambda data, environment: structure.compare_text(None, data, environment)
        elif environment.default_delegate is not None:
            comparer = environment.default_delegate.compare_text
        else:
            raise Exceptions.AttributeNoneError("delegate", self)
        output, has_changes, new_exceptions = comparer(data_extracted, environment)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, has_changes, exceptions
