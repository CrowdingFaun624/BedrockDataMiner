from typing import (TYPE_CHECKING, Any, Callable, Iterable, Iterator,
                    MutableMapping)

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
KEY_WEIGHT = 0.0
VALUE_WEIGHT = 1.0

class KeymapStructure[d](AbstractMappingStructure.AbstractMappingStructure[d]):

    __slots__ = (
        "default_max_similarity_descendent_depth",
        "key_types",
        "key_weights",
        "keys",
        "keys_max_similarity_descendent_depth",
        "keys_with_normalizers",
        "pre_normalized_types",
        "tags",
        "unweighted_keys",
    )

    def __init__(
            self,
            name:str,
            sorting_function:Callable[[tuple[str|D.Diff,Any]],Any]|None,
            min_key_similarity_threshold:float,
            min_value_similarity_threshold:float,
            key_weight:float,
            value_weight:float,
            detect_key_moves:bool,
            key_weights:dict[str,int],
            max_similarity_ancestor_depth:int|None,
            default_max_similarity_descendent_depth:int|None,
            max_key_similarity_descendent_depth:int|None,
            keys_max_similarity_descendent_depth:dict[str,int|None],
            children_has_normalizer:bool,
            children_has_garbage_collection:bool,
        ) -> None:
        super().__init__(name, detect_key_moves, sorting_function, min_key_similarity_threshold, min_value_similarity_threshold, key_weight, value_weight, max_key_similarity_descendent_depth, max_similarity_ancestor_depth, children_has_normalizer, children_has_garbage_collection)

        self.key_weights:dict[str,int] = key_weights
        self.unweighted_keys = {key for key, weight in self.key_weights.items() if weight == 0.0}
        self.default_max_similarity_descendent_depth = default_max_similarity_descendent_depth
        self.keys_max_similarity_descendent_depth = keys_max_similarity_descendent_depth

        self.keys:dict[str,Structure.Structure[d]|None]
        self.tags:dict[str,set[StructureTag.StructureTag]]
        self.key_types:dict[str,tuple[type,...]]
        self.pre_normalized_types:tuple[type,...]
        self.keys_with_normalizers:list[str]

    def link_substructures(
            self,
            keys:dict[str,Structure.Structure|None],
            delegate:"Delegate.Delegate|None",
            key_types:dict[str,tuple[type,...]],
            key_structure:Structure.Structure[str]|None,
            normalizer:list[Normalizer.Normalizer],
            post_normalizer:list[Normalizer.Normalizer],
            pre_normalized_types:tuple[type,...],
            tags:dict[str,set[StructureTag.StructureTag]],
            required_keys:list[str],
            children_tags:set[StructureTag.StructureTag],
        ) -> None:
        super().link_substructures(delegate, key_structure, normalizer, post_normalizer, required_keys, children_tags)
        self.keys = keys
        self.key_types = key_types
        self.pre_normalized_types = pre_normalized_types
        self.tags = tags
        self.keys_with_normalizers = [key for key, substructure in keys.items() if substructure is not None and substructure.children_has_normalizer]

    def get_unweighted_keys(self) -> set[str]:
        return self.unweighted_keys

    def iter_structures(self) -> Iterable[Structure.Structure]:
        return (substructure for substructure in self.keys.values() if substructure is not None)

    def allow_key_move(self, key1: str, value1: d, key2: str, value2: d, exceptions:list[Trace.ErrorTrace]) -> bool:
        structure1, exceptions1 = self.get_structure(key1, value1)
        structure2, exceptions2 = self.get_structure(key2, value2)
        exceptions.extend(exceptions1)
        exceptions.extend(exceptions2)
        return structure1 is structure2

    def get_key_weight(self, key:str, value:d, exceptions:list[Trace.ErrorTrace]) -> int:
        output = self.key_weights.get(key)
        if output is None:
            exceptions.append(Trace.ErrorTrace(Exceptions.StructureUnrecognizedKeyError(key), self.name, key, value))
            return 1
        return output

    def check_type(self, key:str, value:d) -> Trace.ErrorTrace|None:
        if key not in self.key_types:
            return Trace.ErrorTrace(Exceptions.StructureUnrecognizedKeyError(key), self.name, key, value)
        if not isinstance(value, self.key_types[key]):
            return Trace.ErrorTrace(Exceptions.StructureTypeError(tuple(self.key_types[key]), type(value), "Value"), self.name, key, value)

    def get_structure(self, key: str, value:d|None) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        output = self.keys.get(key, ...)
        if output is ...:
            return None, [Trace.ErrorTrace(Exceptions.StructureUnrecognizedKeyError(key), self.name, key, value)]
        return output, []

    def get_tag_paths(self, data: MutableMapping[str, d], tag: StructureTag.StructureTag, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        for key, value in data.items():
            key_tags = self.tags.get(key)
            if key_tags is None:
                exceptions.append(Trace.ErrorTrace(Exceptions.StructureUnrecognizedKeyError(key), self.name, key, value))
                continue
            if tag in key_tags:
                output.append(data_path.copy(key).embed(value))
            structure, new_exceptions = self.get_structure(key, value)
            exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
            if structure is not None:
                new_tags, new_exceptions = structure.get_tag_paths(value, tag, data_path.copy(key), environment)
                output.extend(new_tags)
                exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
        return output, exceptions

    def get_referenced_files(self, data: MutableMapping[str, d], environment: StructureEnvironment.PrinterEnvironment) -> Iterator[int]:
        if not self.children_has_garbage_collection:
            return
        for key, value in data.items():
            structure, new_exceptions = self.get_structure(key, value)
            # for exception in new_exceptions:
            #     print(exception.finalize().stringify())
            # if len(new_exceptions) > 0:
            #     continue
            #     raise RuntimeError()
            if structure is None:
                continue
            yield from structure.get_referenced_files(value, environment)

    def normalize(self, data:dict[str,d], environment:StructureEnvironment.PrinterEnvironment) -> tuple[Any|None,list[Trace.ErrorTrace]]:
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

        for key in self.keys_with_normalizers:
            if key not in data: continue
            value = data[key]
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

    def choose_structure(self, key:str|D.Diff[str], value:d|D.Diff[d]) -> tuple[StructureSet.StructureSet[d], list[Trace.ErrorTrace]]:
        output:dict[tuple[int,...]|None,Structure.Structure|None] = {}
        exceptions:list[Trace.ErrorTrace] = []
        for branches, key_iter, value_iter in D.double_iter_diff(key, value):
            structure = self.keys.get((key_iter), ...)
            if structure is ...:
                exceptions.append(Trace.ErrorTrace(Exceptions.StructureUnrecognizedKeyError(key_iter), self.name, key, value))
                continue
            output[branches] = structure
        return StructureSet.StructureSet(output), exceptions

    def get_max_similarity_descendent_depth(self, key: str) -> int | None:
        return self.keys_max_similarity_descendent_depth.get(key, self.default_max_similarity_descendent_depth)
