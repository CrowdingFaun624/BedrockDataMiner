from typing import TYPE_CHECKING, Any, Callable, Iterable, Iterator, TypeVar, Union

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

a = TypeVar("a")

class FileStructure(ObjectStructure.ObjectStructure[File.AbstractFile[a]]):

    def __init__(self, name: str, children_has_normalizer: bool, children_has_garbage_collection:bool) -> None:
        super().__init__(name, children_has_normalizer, children_has_garbage_collection)

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

    def get_similarity(self, data1: File.AbstractFile[a], data2: File.AbstractFile[a], environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace]) -> float:
        if self.structure is None:
            return float(data1 == data2)
        else:
            output = self.structure.get_similarity(data1.data, data2.data, environment, exceptions)
            return output

    def compare(self, data1:File.AbstractFile[a], data2:File.AbstractFile[a], environment:StructureEnvironment.ComparisonEnvironment) -> tuple[a|D.Diff[a, a], bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        if self.structure is None:
            if data1 is data2 or data1 == data2:
                output, has_changes = data1.data, False
            else:
                output, has_changes = D.Diff(data1.data, data2.data), True
        else:
            output, has_changes, new_exceptions = self.structure.compare(data1.data, data2.data, environment)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
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

    def compare_text(self, data:File.AbstractFile[a]|D.Diff[File.AbstractFile[a],File.AbstractFile[a]], environment:StructureEnvironment.ComparisonEnvironment) -> tuple[Any, bool, list[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        if isinstance(data, D.Diff):
            match data.change_type:
                case D.ChangeType.removal:
                    data_extracted = D.Diff(old=data.old.data)
                case D.ChangeType.change:
                    data_extracted = D.Diff(old=data.old.data, new=data.new.data)
                case D.ChangeType.addition:
                    data_extracted = D.Diff(new=data.new.data)
        else:
            data_extracted = data.data
        structure, new_exceptions = self.choose_structure(None, data_extracted)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        comparer:Callable[[Any, StructureEnvironment.ComparisonEnvironment],tuple[Any,bool,list[Trace.ErrorTrace]]]
        if self.delegate is not None:
            comparer = self.delegate.compare_text
        elif structure is not None and structure[D.DiffType.not_diff] is not None:
            comparer = lambda data, environment: structure.compare_text(D.DiffType.not_diff, data, environment)
        elif environment.default_delegate is not None:
            comparer = environment.default_delegate.compare_text
        else:
            raise Exceptions.AttributeNoneError("delegate", self)
        output, has_changes, new_exceptions = comparer(data_extracted, environment)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, has_changes, exceptions
