from typing import Any, Callable, Iterable, MutableMapping, TypeVar

import Structure.AbstractMappingStructure as AbstractMappingStructure
import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

d = TypeVar("d")

MIN_KEY_SIMILARITY_THRESHOLD = 0.0
MIN_VALUE_SIMILARITY_THRESHOLD = 0.5

class KeymapStructure(AbstractMappingStructure.AbstractMappingStructure[d]):

    def __init__(
            self,
            name:str,
            field:str,
            measure_length:bool,
            print_all:bool,
            sorting_function:Callable[[tuple[str|D.Diff,Any]],Any]|None,
            min_key_similarity_threshold:float,
            min_value_similarity_threshold:float,
            detect_key_moves:bool,
            children_has_normalizer:bool,
            children_tags:set[str],
        ) -> None:
        super().__init__(name, field, detect_key_moves, None, measure_length, print_all, sorting_function, min_key_similarity_threshold, min_value_similarity_threshold, children_has_normalizer, children_tags)

        self.keys:dict[str,Structure.Structure[d]|None]|None = None
        self.tags:dict[str,list[str]]|None = None
        self.key_types:dict[str,tuple[type,...]]|None = None
        self.keys_with_normalizers:list[str]|None = None

    def link_substructures(
            self,
            keys:dict[str,Structure.Structure|None],
            key_types:dict[str,tuple[type,...]],
            normalizer:list[Normalizer.Normalizer],
            tags:dict[str,list[str]],
            keys_with_normalizers:list[str],
        ) -> None:
        self.keys = keys
        self.key_types = key_types
        self.normalizer = normalizer
        self.tags = tags
        self.keys_with_normalizers = keys_with_normalizers

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.keys is None:
            raise Exceptions.AttributeNoneError("keys", self)
        return (substructure for substructure in self.keys.values() if substructure is not None)

    def check_type(self, key:str, value:d) -> Trace.ErrorTrace|None:
        if self.key_types is None:
            raise Exceptions.AttributeNoneError("key_types", self)
        if key not in self.key_types:
            return Trace.ErrorTrace(Exceptions.StructureUnrecognizedKeyError(key), self.name, key, value)
        if not isinstance(value, self.key_types[key]):
            return Trace.ErrorTrace(Exceptions.StructureTypeError(tuple(self.key_types[key]), type(value), "Value"), self.name, key, value)

    def get_structure(self, key: str, value:d|None) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        if self.keys is None:
            raise Exceptions.AttributeNoneError("keys", self)
        output = self.keys.get(key, Structure.StructureFailure.choose_structure_failure)
        if output is Structure.StructureFailure.choose_structure_failure:
            return None, [Trace.ErrorTrace(Exceptions.StructureUnrecognizedKeyError(key), self.name, key, value)]
        return output, []

    def get_tag_paths(self, data: MutableMapping[str, d], tag: str, data_path: DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        if tag not in self.children_tags: return [], []
        output:list[DataPath.DataPath] = []
        exceptions:list[Trace.ErrorTrace] = []
        if self.tags is None:
            raise Exceptions.AttributeNoneError("tags", self)
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

    def normalize(self, data:dict[str,d], environment:StructureEnvironment.StructureEnvironment) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        if not self.children_has_normalizer: return None, []
        if self.normalizer is None:
            raise Exceptions.AttributeNoneError("normalizer", self)
        if self.keys_with_normalizers is None:
            raise Exceptions.AttributeNoneError("keys_with_normalizers", self)
        for normalizer in self.normalizer:
            try:
                normalizer(data)
            except Exception as e:
                return None, [Trace.ErrorTrace(e, self.name, None, data)]
        exceptions:list[Trace.ErrorTrace] = []
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
        return None, exceptions

    def choose_structure(self, key:str, value:d) -> tuple[StructureSet.StructureSet, list[Trace.ErrorTrace]]:
        if self.keys is None:
            raise Exceptions.AttributeNoneError("keys", self)
        output:dict[D.DiffType,Structure.Structure|None] = {}
        exceptions:list[Trace.ErrorTrace] = []
        if self.detect_key_moves:
            iterator = D.double_iter_diff(key, value)
        else:
            key_iter = key.first_existing_property() if isinstance(key, D.Diff) else key
            iterator = ((key_iter, iter_diff_item[0], None, iter_diff_item[1]) for iter_diff_item in D.iter_diff(value))
        for key_iter, value_iter, key_diff_type, value_diff_type in iterator:
            structure = self.keys.get((key_iter), Structure.StructureFailure.choose_structure_failure)
            if structure is Structure.StructureFailure.choose_structure_failure:
                exceptions.append(Trace.ErrorTrace(Exceptions.StructureUnrecognizedKeyError(key), self.name, key, value))
                continue
            output[value_diff_type] = structure
        return StructureSet.StructureSet(output), exceptions
