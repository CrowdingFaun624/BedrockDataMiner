from typing import (TYPE_CHECKING, Any, Callable, Iterable, Iterator,
                    MutableMapping, Union)

import Structure.AbstractMappingStructure as AbstractMappingStructure
import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate

MIN_KEY_SIMILARITY_THRESHOLD = 0.0
MIN_VALUE_SIMILARITY_THRESHOLD = 0.5
KEY_WEIGHT = 0.2
VALUE_WEIGHT = 0.8

class DictStructure[d](AbstractMappingStructure.AbstractMappingStructure[d]):

    __slots__ = (
        "max_similarity_descendent_depth",
        "pre_normalized_types",
        "structure",
        "tags",
        "types",
    )

    def __init__(
            self,
            name:str,
            detect_key_moves:bool,
            sorting_function:Callable[[tuple[str|D.Diff,Any]],Any]|None,
            min_key_similarity_threshold:float,
            min_value_similarity_threshold:float,
            key_weight:float,
            value_weight:float,
            max_key_similarity_descendent_depth:int|None,
            max_similarity_descendent_depth:int|None,
            max_similarity_ancestor_depth:int|None,
            children_has_normalizer:bool,
            children_has_garbage_collection:bool,
        ) -> None:
        super().__init__(name, detect_key_moves, sorting_function, min_key_similarity_threshold, min_value_similarity_threshold, key_weight, value_weight, max_key_similarity_descendent_depth, max_similarity_ancestor_depth, children_has_normalizer, children_has_garbage_collection)

        self.max_similarity_descendent_depth = max_similarity_descendent_depth

        self.structure:Structure.Structure[d]|None = None
        self.types:tuple[type,...]|None = None
        self.pre_normalized_types:tuple[type,...]|None = None
        self.tags:set[StructureTag.StructureTag]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure[d]|None,
        delegate:Union["Delegate.Delegate", None],
        key_structure:Structure.Structure[str]|None,
        types:tuple[type,...],
        normalizer:list[Normalizer.Normalizer],
        post_normalizer:list[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
        tags:set[StructureTag.StructureTag],
        required_keys:list[str],
        children_tags:set[StructureTag.StructureTag],
    ) -> None:
        super().link_substructures(delegate, key_structure, normalizer, post_normalizer, required_keys, children_tags)
        self.structure = structure
        self.types = tuple(types)
        self.pre_normalized_types = tuple(pre_normalized_types)
        self.tags = tags

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.structure is None: return []
        else: return [self.structure]

    def check_type(self, key:str, value:d) -> Trace.ErrorTrace|None:
        if self.types is None:
            raise Exceptions.AttributeNoneError("types", self)
        if not isinstance(value, self.types):
            return Trace.ErrorTrace(Exceptions.StructureTypeError(self.types, type(value), "Value"), self.name, key, value)

    def get_tag_paths(self, data: MutableMapping[str, d], tag: StructureTag.StructureTag, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        if self.children_tags is None:
            raise Exceptions.AttributeNoneError("children_tags", self)
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        if self.tags is None:
            raise Exceptions.AttributeNoneError("tags", self)
        if tag in self.tags:
            output.extend(data_path.copy(key).embed(value) for key, value in data.items())
        for key, value in data.items():
            structure, new_exceptions = self.get_structure(key, value)
            exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
            if structure is not None:
                new_tags, new_exceptions = structure.get_tag_paths(value, tag, data_path.copy(key), environment)
                output.extend(new_tags)
                exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
        return output, exceptions

    def get_referenced_files(self, data: MutableMapping[str, d], environment: StructureEnvironment.PrinterEnvironment) -> Iterator[int]:
        if self.structure is not None and self.children_has_garbage_collection:
            for value in data.values():
                yield from self.structure.get_referenced_files(value, environment)

    def normalize(self, data:dict[str,d], environment:StructureEnvironment.PrinterEnvironment) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        if not self.children_has_normalizer: return None, []
        if self.normalizer is None:
            raise Exceptions.AttributeNoneError("normalizer", self)
        if self.post_normalizer is None:
            raise Exceptions.AttributeNoneError("post_normalizer", self)
        if self.pre_normalized_types is None:
            raise Exceptions.AttributeNoneError("pre_normalized_types", self)
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

        for key, value in data.items():
            structure, new_exceptions = self.get_structure(key, value)
            exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
            if structure is not None and structure.children_has_normalizer:
                normalizer_output, new_exceptions = structure.normalize(value, environment)
                exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
                if normalizer_output is not None:
                    data[key] = normalizer_output

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

    def get_structure(self, key:str, value:d) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        return self.structure, []

    def choose_structure(self, key:str|D.Diff[str], value:d|D.Diff[d]) -> tuple[StructureSet.StructureSet[d], list[Trace.ErrorTrace]]:
        return StructureSet.StructureSet({value_branch: self.structure for value_branch, value_iter in D.iter_diff(value)}), []

    def get_max_similarity_descendent_depth(self, key: str) -> int | None:
        return self.max_similarity_descendent_depth
