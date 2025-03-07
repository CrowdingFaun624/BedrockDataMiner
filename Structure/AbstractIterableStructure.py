from typing import TYPE_CHECKING, Any, Iterable, Iterator, Sequence

import Structure.DataPath as DataPath
import Structure.Normalizer as Normalizer
import Structure.ObjectStructure as ObjectStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate

class AbstractIterableStructure[d](ObjectStructure.ObjectStructure[Sequence[d]]):
    """
    Abstract class of list-using Structures.
    Must override `compare`, `get_similarity`, `get_item_key`, and `get_compare_text_key_str`.
    """

    __slots__ = (
        "max_similarity_ancestor_depth",
        "max_similarity_descendent_depth",
        "normalizer",
        "post_normalizer",
        "pre_normalized_types",
        "structure",
        "tags",
        "types",
    )

    def __init__(
            self,
            name:str,
            max_similarity_descendent_depth:int|None,
            max_similarity_ancestor_depth:int|None,
            children_has_normalizer:bool,
            children_has_garbage_collection:bool,
        ) -> None:
        super().__init__(name, children_has_normalizer, children_has_garbage_collection)

        self.max_similarity_descendent_depth = max_similarity_descendent_depth
        self.max_similarity_ancestor_depth = max_similarity_ancestor_depth

        self.structure:Structure.Structure[d]|None
        self.types:tuple[type,...]
        self.normalizer:list[Normalizer.Normalizer]
        self.post_normalizer:list[Normalizer.Normalizer]
        self.pre_normalized_types:tuple[type,...]
        self.tags:set[StructureTag.StructureTag]

    def link_substructures(
        self,
        structure:Structure.Structure[d]|None,
        delegate:"Delegate.Delegate|None",
        types:tuple[type,...],
        normalizer:list[Normalizer.Normalizer],
        post_normalizer:list[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
        tags:set[StructureTag.StructureTag],
        children_tags:set[StructureTag.StructureTag],
    ) -> None:
        super().link_substructures(delegate, children_tags)
        self.structure = structure
        self.types = types
        self.normalizer = normalizer
        self.post_normalizer = post_normalizer
        self.pre_normalized_types = pre_normalized_types
        self.tags = tags

    def get_structure(self, key:int, value:d) -> tuple[Structure.Structure[d]|None, list[Trace.ErrorTrace]]:
        return self.structure, []

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.structure is None: return []
        else: return [self.structure]

    def check_type(self, index:int, item:d) -> Trace.ErrorTrace|None:
        if not isinstance(item, self.types):
            return Trace.ErrorTrace(Exceptions.StructureTypeError(self.types, type(item), "Item"), self.name, index, item)

    def check_all_types(self, data:list[d], environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[Trace.ErrorTrace] = []
        for index, item in enumerate(data):
            check_type_output = self.check_type(index, item)
            if check_type_output is not None:
                output.append(check_type_output)
                continue

            if self.structure is not None:
                output.extend(exception.add(self.name, index) for exception in self.structure.check_all_types(item, environment))
        return output

    def normalize(self, data:list[d], environment:StructureEnvironment.PrinterEnvironment) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        if not self.children_has_normalizer: return None, []
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

        for index, item in enumerate(data):
            if self.structure is not None:
                normalizer_output, new_exceptions = self.structure.normalize(item, environment)
                exceptions.extend(exception.add(self.name, index) for exception in new_exceptions)
                if normalizer_output is not None:
                    data[index] = normalizer_output

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

    def get_tag_paths(self, data: list[d], tag: StructureTag.StructureTag, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        if tag in self.tags:
            output.extend(data_path.copy(index).embed(value) for index, value in enumerate(data))
        for index, value in enumerate(data):
            if self.structure is not None:
                new_tags, new_exceptions = self.structure.get_tag_paths(value, tag, data_path.copy(index), environment)
                output.extend(new_tags)
                exceptions.extend(exception.add(self.name, index) for exception in new_exceptions)
        return output, exceptions

    def get_referenced_files(self, data: Sequence[d], environment: StructureEnvironment.PrinterEnvironment) -> Iterator[int]:
        if self.structure is not None and self.children_has_garbage_collection:
            for value in data:
                yield from self.structure.get_referenced_files(value, environment)
