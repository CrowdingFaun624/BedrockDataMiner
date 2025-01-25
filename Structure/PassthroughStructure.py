from typing import TYPE_CHECKING, Any, Callable, Iterable, Iterator, Sequence

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.ObjectStructure as ObjectStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate

class PassthroughStructure[a](ObjectStructure.ObjectStructure[a]):
    '''
    Simply passes data through itself. Can be subclassed.
    Not all Structures that have this behavior have to subclass this class.
    '''

    __slots__ = (
        "max_similarity_ancestor_depth",
        "max_similarity_descendent_depth",
        "types",
        "normalizer",
        "post_normalizer",
        "pre_normalized_types",
    )

    def __init__(
        self,
        name:str,
        max_similarity_ancestor_depth:int|None,
        max_similarity_descendent_depth:int|None,
        children_has_normalizer:bool,
        children_has_garbage_collection:bool,
    ) -> None:
        super().__init__(name, children_has_normalizer, children_has_garbage_collection)

        self.max_similarity_ancestor_depth = max_similarity_ancestor_depth
        self.max_similarity_descendent_depth = max_similarity_descendent_depth

        self.types:tuple[type,...]
        self.normalizer:Sequence[Normalizer.Normalizer]
        self.post_normalizer:Sequence[Normalizer.Normalizer]
        self.pre_normalized_types:tuple[type,...]

    def link_substructures(
        self,
        delegate:"Delegate.Delegate|None",
        types:tuple[type,...],
        normalizer:Sequence[Normalizer.Normalizer],
        post_normalizer:Sequence[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
        children_tags: set[StructureTag.StructureTag],
    ) -> None:
        super().link_substructures(delegate, children_tags)
        self.types = types
        self.normalizer = normalizer
        self.post_normalizer = post_normalizer
        self.pre_normalized_types = pre_normalized_types

    def iter_structures(self) -> Iterable[Structure.Structure]:
        ...

    def check_all_types(self, data:a, environment:StructureEnvironment.StructureEnvironment) -> Sequence[Trace.ErrorTrace]:
        output:list[Trace.ErrorTrace] = []
        if not isinstance(data, self.types):
            output.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.types, type(data), "Data"), self.name, None, data))
            return output
        structure, new_exceptions = self.get_structure(None, data)
        output.extend(exception.add(self.name, None) for exception in new_exceptions)
        if structure is not None:
            output.extend(exception.add(self.name, None) for exception in structure.check_all_types(data, environment))
        return output

    def normalize(self, data:a, environment:StructureEnvironment.PrinterEnvironment) -> tuple[Any|None, Sequence[Trace.ErrorTrace]]:
        if not self.children_has_normalizer: return None, ()
        exceptions:list[Trace.ErrorTrace] = []
        if not isinstance(data, self.pre_normalized_types):
            exceptions.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"), self.name, None, data))
            return None, exceptions

        data_identity_changed = False
        for normalizer in self.normalizer:
            if normalizer.version_range is not None and environment.get_version() not in normalizer.version_range: continue
            try:
                normalizer_output = normalizer(data)
                if normalizer_output is not None:
                    data_identity_changed = True
                    data = normalizer_output
            except Exception as e:
                exceptions.append(Trace.ErrorTrace(e, self.name, None, data))

        structure, new_exceptions = self.get_structure(None, data)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        if structure is not None:
            normalizer_output, new_exceptions = structure.normalize(data, environment)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
            if normalizer_output is not None:
                data_identity_changed = True
                data = normalizer_output

        for normalizer in self.post_normalizer:
            if normalizer.version_range is not None and environment.get_version() not in normalizer.version_range: continue
            try:
                normalizer_output = normalizer(data)
                if normalizer_output is not None:
                    data_identity_changed = True
                    data = normalizer_output
            except Exception as e:
                exceptions.append(Trace.ErrorTrace(e, self.name, None, data))
                return None, exceptions

        if data_identity_changed:
            return data, exceptions
        else:
            return None, exceptions

    def get_tag_paths(self, data:a, tag: StructureTag.StructureTag, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[Sequence[DataPath.DataPath], Sequence[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return (), ()
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.get_structure(None, data)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        if structure is None:
            return (), exceptions
        output, new_exceptions = structure.get_tag_paths(data, tag, data_path.copy(), environment)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, exceptions

    def get_referenced_files(self, data: a, environment: StructureEnvironment.PrinterEnvironment) -> Iterator[int]:
        structure, _ = self.get_structure(None, data)
        if structure is not None and self.children_has_garbage_collection:
            yield from structure.get_referenced_files(data, environment)

    def get_similarity(self, data1: a, data2: a, depth:int, max_depth:int|None, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace], branch:int) -> float:
        structure1, exceptions1 = self.get_structure(None, data1)
        structure2, exceptions2 = self.get_structure(None, data2)
        if len(exceptions1) > 0 or len(exceptions2) > 0:
            similarity_exceptions:list[Trace.ErrorTrace] = []
            similarity_exceptions.extend(exceptions1)
            similarity_exceptions.extend(exceptions2)
            exceptions.append(Trace.ErrorTrace(Exceptions.StructureExceptionError(self, self.get_similarity, similarity_exceptions), self.name, None, (data1, data2)))
        if (max_depth is not None and depth > max_depth) or (self.max_similarity_ancestor_depth is not None and depth > self.max_similarity_ancestor_depth) or structure1 is None or structure1 is not structure2:
            if branch == 0:
                return float(data1 == data2)
            else:
                return float(Structure.get_data_at_branch(data1, branch) == data2)
        else:
            output = structure1.get_similarity(data1, data2, depth, max_depth, environment, exceptions, branch)
            return output

    def compare(self, data1:a, data2:a, environment:StructureEnvironment.ComparisonEnvironment, branch:int, branches:int) -> tuple[a|D.Diff[a], bool, Sequence[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        structure1, new_exceptions = self.get_structure(None, data1)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        structure2, new_exceptions = self.get_structure(None, data2)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        if structure1 is None or structure1 is not structure2:
            if data1 is data2 or data1 == data2:
                output, has_changes = data1, False
            else:
                output, has_changes = D.Diff(branches, {tuple(range(0,branch+1)): data1, (branch+1,): data2}), True
        else:
            output, has_changes, new_exceptions = structure1.compare(data1, data2, environment, branch, branches)
            exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, has_changes, exceptions

    def print_text(self, data: a, environment:StructureEnvironment.PrinterEnvironment) -> tuple[Any, Sequence[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.get_structure(None, data)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        if self.delegate is not None:
            printer = self.delegate
        elif structure is not None:
            printer = structure
        elif environment.default_delegate is not None:
            printer = environment.default_delegate
        else:
            raise Exceptions.InvalidStateError(self)
        output, new_exceptions = printer.print_text(data, environment)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, exceptions

    def compare_text(self, data:a|D.Diff[a], environment:StructureEnvironment.ComparisonEnvironment) -> tuple[Any, bool, Sequence[Trace.ErrorTrace]]:
        exceptions:list[Trace.ErrorTrace] = []
        structure, new_exceptions = self.choose_structure(None, data)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        comparer:Callable[[Any, StructureEnvironment.ComparisonEnvironment],tuple[Any,bool,list[Trace.ErrorTrace]]]
        if self.delegate is not None:
            comparer = self.delegate.compare_text
        elif structure is not None and structure[None] is not None:
            comparer = lambda data, environment: structure.compare_text(None, data, environment)
        elif environment.default_delegate is not None:
            comparer = environment.default_delegate.compare_text
        else:
            raise Exceptions.InvalidStateError(self)
        output, has_changes, new_exceptions = comparer(data, environment)
        exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
        return output, has_changes, exceptions
