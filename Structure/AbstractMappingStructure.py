from types import EllipsisType
from typing import (TYPE_CHECKING, Any, Callable, MutableMapping, TypeVar,
                    Union, cast)

import Structure.Difference as D
import Structure.Hashing as Hashing
import Structure.Normalizer as Normalizer
import Structure.ObjectStructure as ObjectStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.Nbt.NbtTypes as NbtTypes

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate

d = TypeVar("d")

class AbstractMappingStructure(ObjectStructure.ObjectStructure[MutableMapping[str, d]]):
    """
    Abstract class of dict-using Structures.
    In subclasses, must provide methods `iter_structures`, `check_type`,
    `get_structure`, `choose_structure`, `get_tag_paths`,
    `get_referenced_files`, `normalize`, and `get_max_similarity_descendent_depth`.
    """

    valid_types = (dict, NbtTypes.TAG_Compound)

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
            max_similarity_ancestor_depth:int|None,
            children_has_normalizer:bool,
            children_has_garbage_collection:bool,
        ) -> None:
        super().__init__(name, children_has_normalizer, children_has_garbage_collection)

        self.detect_key_moves = detect_key_moves
        self.sorting_function = sorting_function
        self.min_key_similarity_threshold = min_key_similarity_threshold
        self.min_value_similarity_threshold = min_value_similarity_threshold
        self.key_weight = key_weight
        self.value_weight = value_weight
        self.max_key_similarity_descendent_depth = max_key_similarity_descendent_depth
        self.max_similarity_ancestor_depth = max_similarity_ancestor_depth
        # get_max_similarity_descendent_depth is defined by each subclass

        self.key_structure:Structure.Structure[str]|None = None
        self.normalizer:list[Normalizer.Normalizer]|None = None
        self.post_normalizer:list[Normalizer.Normalizer]|None = None

    def link_substructures(
        self,
        delegate:Union["Delegate.Delegate", None],
        key_structure:Structure.Structure[str]|None,
        normalizer:list[Normalizer.Normalizer],
        post_normalizer:list[Normalizer.Normalizer],
        required_keys:list[str],
        children_tags:set[StructureTag.StructureTag],
    ) -> None:
        super().link_substructures(delegate, children_tags)
        self.delegate = delegate
        self.key_structure = key_structure
        self.normalizer = normalizer
        self.post_normalizer = post_normalizer
        self.required_keys = required_keys

    def check_type(self, key:str, value:d) -> Trace.ErrorTrace|None: ...

    def get_structure(self, key:str, value:d) -> tuple[Structure.Structure[d]|None, list[Trace.ErrorTrace]]:
        '''
        Returns a substructure or None.
        :key: The key of this Structure at the current position.
        :value: The value at the current position.
        '''
        ...

    def choose_structure(self, key:str|D.Diff[str], value:d|D.Diff[d]) -> tuple[StructureSet.StructureSet, list[Trace.ErrorTrace]]: ...

    def check_all_types(self, data:MutableMapping[str,d], environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[Trace.ErrorTrace] = []
        if not isinstance(data, self.valid_types):
            output.append(Trace.ErrorTrace(Exceptions.StructureTypeError(self.valid_types, type(data), "Data"), self.name, None, data))
            return output
        for key, value in data.items():
            if (check_type_output := self.check_type(key, value)) is not None:
                output.append(check_type_output)
                continue

            structure, new_exceptions = self.get_structure(key, value)
            output.extend(exception.add(self.name, key) for exception in new_exceptions)
            if structure is not None:
                output.extend(exception.add(self.name, key) for exception in structure.check_all_types(value, environment))
        for key in self.required_keys:
            if key not in data:
                output.append(Trace.ErrorTrace(Exceptions.StructureRequiredKeyMissingError(self, key), self.name, None, data))
        return output

    def get_max_similarity_descendent_depth(self, key:str) -> int|None: ...

    def get_unweighted_keys(self) -> set[str]:
        '''
        Returns keys that are unweighted and thus should not be used for similarity.
        '''
        return set()

    def get_similarity(self, data1: MutableMapping[str, d], data2: MutableMapping[str, d], depth:int, max_depth:int|None, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace]) -> float:
        if (max_depth is not None and depth > max_depth) or (self.max_similarity_ancestor_depth is not None and depth > self.max_similarity_ancestor_depth):
            return float(data1 == data2)
        data1_hashes:dict[int,tuple[str,d]] = {Hashing.hash_data((key, value)): (key, value) for key, value in data1.items()}
        data2_hashes:dict[int,tuple[str,d]] = {Hashing.hash_data((key, value)): (key, value) for key, value in data2.items()}

        same_keys = data1.keys() & data2.keys() # keys present in both old and new data.
        same_hashes = data1_hashes.keys() & data2_hashes.keys()
        data1_exclusive_items = {exclusive_hash: data1_hashes[exclusive_hash] for exclusive_hash in data1_hashes.keys() - data2_hashes.keys()}
        data2_exclusive_items = {exclusive_hash: data2_hashes[exclusive_hash] for exclusive_hash in data2_hashes.keys() - data1_hashes.keys()}

        similarity_count = sum(self.get_key_weight(data1_hashes[hash][0], data1, exceptions) for hash in same_hashes)
        total_weight = sum(self.get_key_weight(key, data2, exceptions) for key in data1.keys() | data2.keys())
        if len(data1_exclusive_items) > 0 and len(data2_exclusive_items) > 0 and total_weight != 0:
            already_data1_hashes:set[int] = set() # items of data1_hashes that have already been picked.
            already_data2_hashes:set[int] = set() # items of data2_hashes that have already been picked.
            for hash1, hash2, key_similarity, value_similarity, key1, key2 in self.get_similarities_list(data1_exclusive_items, data2_exclusive_items, same_keys, depth, max_depth, environment, exceptions):
                if hash1 in already_data1_hashes or hash2 in already_data2_hashes or not self.allow_key_move(key1, data1[key1], key2, data2[key2], exceptions):
                    if len(already_data1_hashes) == len(data1_exclusive_items) or len(already_data2_hashes) == len(data2_exclusive_items):
                        break
                    continue
                already_data1_hashes.add(hash1)
                already_data2_hashes.add(hash2)
                similarity_count += ((self.get_key_weight(key1, data1, exceptions) + self.get_key_weight(key2, data2, exceptions))) * ((key_similarity * self.key_weight + value_similarity * self.value_weight)) / (2 * (self.key_weight + self.value_weight))
        similarity = similarity_count / total_weight if total_weight != 0 else 1.0
        if similarity < 0.0 or similarity > 1.0:
            exceptions.append(Trace.ErrorTrace(Exceptions.InvalidSimilarityError(self, similarity, data1, data2), self.name, None, (data1, data2)))
        return similarity

    def get_key_similarity(self, key1:str, key2:str, depth:int, max_depth:int|None|EllipsisType, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace]) -> float:
        '''
        Gets the similarity between two keys of this Structure's data.
        :key1: The key of the older key-value pair.
        :key2: The key of the newer key-value pair.
        :environment: The StructureEnvironment to use.
        '''
        if key1 == key2:
            return 1.0
        elif self.key_structure is not None:
            if max_depth is ...:
                max_depth = self.max_key_similarity_descendent_depth
            return self.key_structure.get_similarity(key1, key2, depth + 1, max_depth, environment, exceptions)
        else:
            return 0.0

    def get_value_similarity(self, key1:str, value1:d, key2:str, value2:d, depth:int, max_depth:int|None|EllipsisType, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace]) -> float:
        '''
        Gets the similarity between two values of this Structure's data.
        :key1: The key of the older key-value pair.
        :value1: The value of the older key-value pair.
        :key2: The key of the newer key-value pair.
        :value2: The value of the newer key-value pair.
        :environment: The StructureEnvironment to use.
        '''
        if value1 == value2:
            return 1.0
        structure1, exceptions1 = self.get_structure(key1, value1)
        structure2, exceptions2 = self.get_structure(key2, value2)
        exceptions.extend(exceptions1)
        exceptions.extend(exceptions2)
        if structure1 is structure2 and structure1 is not None:
            if max_depth is ...:
                if key1 == key2:
                    max_depth = self.get_max_similarity_descendent_depth(key1)
                else:
                    max_similarity_descendent_depth1 = self.get_max_similarity_descendent_depth(key1)
                    max_similarity_descendent_depth2 = self.get_max_similarity_descendent_depth(key2)
                    max_depth = (None if max_similarity_descendent_depth1 is None else max_similarity_descendent_depth1) if max_similarity_descendent_depth2 is None else (max_similarity_descendent_depth2 if max_similarity_descendent_depth1 is None else min(max_similarity_descendent_depth2, max_similarity_descendent_depth1))
            output = structure1.get_similarity(value1, value2, depth + 1, max_depth, environment, exceptions)
        else:
            output = 0.0
        return output

    def allow_key_move(self, key1:str, value1:d, key2:str, value2:d, exceptions:list[Trace.ErrorTrace]) -> bool:
        '''
        Returns True if the key in key1 may move to key2.
        :key1: The older key.
        :value1: The older value.
        :key2: The newer key.
        :value2: The newer value.
        '''
        return True

    def get_key_weight(self, key:str, data:MutableMapping[str, d], exceptions:list[Trace.ErrorTrace]) -> int:
        '''
        Returns the weight that the key has in similarity calculations.
        '''
        return 1

    def get_similarities_list(
        self,
        data1_exclusive_items:dict[int,tuple[str,d]],
        data2_exclusive_items:dict[int,tuple[str,d]],
        same_keys:set[str],
        depth:int,
        max_depth:int|None|EllipsisType,
        environment:StructureEnvironment.ComparisonEnvironment,
        exceptions:list[Trace.ErrorTrace],
    ) -> list[tuple[int,int,float,float,str,str]]:
        keys1_hashes = {key1: (hash1, value1) for hash1, (key1, value1) in data1_exclusive_items.items()}
        keys2_hashes = {key2: (hash2, value2) for hash2, (key2, value2) in data2_exclusive_items.items()}
        unweighted_keys = self.get_unweighted_keys()
        same_keys_list:list[tuple[int, int, float, float, str, str]] = [
            (
                keys1_hashes[key][0],
                keys2_hashes[key][0],
                1.0,
                (self.get_value_similarity(key, keys1_hashes[key][1], key, keys2_hashes[key][1], depth, max_depth, environment, exceptions) if key not in unweighted_keys else 1.0),
                # if this is for similarity, then the 1.0 when unweighted won't matter because it'll be multiplied by 0 anyways.
                # if this is for comparison, then these keys have to be together anyway, so it doesn't matter what the value similarity is.
                key,
                key,
            )
            for key in same_keys
            if key in keys1_hashes # same_keys has all keys that are similar, not just ones with different values.
        ]
        if self.detect_key_moves:
            similarities_list:list[tuple[int, int, float, float, str, str]] = [ # maps similarity of older items to newer items
                (hash1, hash2, key_similarity, value_similarity, key1, key2)
                for hash1, (key1, value1) in data1_exclusive_items.items()
                if key1 not in same_keys and key1 not in unweighted_keys
                for hash2, (key2, value2) in data2_exclusive_items.items()
                if key2 not in same_keys and key2 not in unweighted_keys and self.allow_key_move(key1, value1, key2, value2, exceptions)
                # key1 cannot equal key2
                if (key_similarity := self.get_key_similarity(key1, key2, depth, max_depth, environment, exceptions)) >= self.min_key_similarity_threshold
                if (value_similarity := self.get_value_similarity(key1, value1, key2, value2, depth, max_depth, environment, exceptions)) > self.min_value_similarity_threshold
            ]
        else:
            similarities_list = []
        output = same_keys_list + similarities_list
        # sort by weighted similarities using the thresholds.
        output.sort(key=lambda item: ((item[2] * self.key_weight + item[3] * self.value_weight) / (self.key_weight + self.value_weight), item[4], item[5]), reverse=True)
        return output

    def compare(
            self,
            data1:MutableMapping[str,d],
            data2:MutableMapping[str,d],
            environment:StructureEnvironment.ComparisonEnvironment,
        ) -> tuple[MutableMapping[str|D.Diff[str],d|D.Diff[d]],bool,list[Trace.ErrorTrace]]:

        if data1 is data2 or data1 == data2:
            return cast(Any, data1), False, []
        exceptions:list[Trace.ErrorTrace] = []

        data1_hashes:dict[int,tuple[str,d]] = {Hashing.hash_data((key, value)): (key, value) for key, value in data1.items()}
        data2_hashes:dict[int,tuple[str,d]] = {Hashing.hash_data((key, value)): (key, value) for key, value in data2.items()}

        same_keys = data1.keys() & data2.keys() # keys that existed both before and after.
        same_hashes = [hash for hash in data1_hashes.keys() if hash in data2_hashes] # retain order
        data1_exclusive_items = {exclusive_hash: data1_hashes[exclusive_hash] for exclusive_hash in data1_hashes if exclusive_hash not in data2_hashes}
        data2_exclusive_items = {exclusive_hash: data2_hashes[exclusive_hash] for exclusive_hash in data2_hashes if exclusive_hash not in data1_hashes}
        output:dict[str|D.Diff,d|D.Diff] = cast(Any, type(data1)())
        has_changes = len(data1_exclusive_items) > 0 or len(data2_exclusive_items) > 0

        # unchanged items
        output.update(data1_hashes[same_hash] for same_hash in same_hashes)

        # changed items
        already_data1_hashes:set[int] = set() # items of data1_hashes that have already been picked.
        already_data2_hashes:set[int] = set() # items of data2_hashes that have already been picked.
        if len(data1_exclusive_items) > 0 and len(data2_exclusive_items) > 0:
            for hash1, hash2, _, _, _, _ in self.get_similarities_list(data1_exclusive_items, data2_exclusive_items, same_keys, 1, ..., environment, exceptions):
                # I use max_depth=None because it'll be set to the correct value in get_value_similarity.
                if hash1 in already_data1_hashes or hash2 in already_data2_hashes:
                    if len(already_data1_hashes) == len(data1_exclusive_items) or len(already_data2_hashes) == len(data2_exclusive_items):
                        break
                    continue # if either side is already involved in a change, it's unneeded.
                already_data1_hashes.add(hash1)
                already_data2_hashes.add(hash2)
                key1, value1 = data1_exclusive_items[hash1]
                key2, value2 = data2_exclusive_items[hash2]
                structure1, new_exceptions = self.get_structure(key1, value1)
                exceptions.extend(exception.add(self.name, key1) for exception in new_exceptions)
                structure2, new_exceptions = self.get_structure(key2, value2)
                exceptions.extend(exception.add(self.name, key2) for exception in new_exceptions)
                if key1 == key2:
                    key_compare_output = key1
                else:
                    key_compare_output = D.Diff(key1, key2)
                if value1 is value2 or value1 == value2:
                    value_compare_output = value1
                elif structure1 is not structure2 or structure1 is None:
                    value_compare_output = D.Diff(value1, value2)
                else:
                    value_compare_output, _, new_exceptions = structure1.compare(value1, value2, environment)
                    exceptions.extend(exception.add(self.name, key2) for exception in new_exceptions)
                output[key_compare_output] = value_compare_output

        # added/removed items
        output.update(
            (D.Diff(old=key), D.Diff(old=value))
            for exclusive_hash, (key, value) in data1_exclusive_items.items()
            if exclusive_hash not in already_data1_hashes
        )
        output.update(
            (D.Diff(new=key), D.Diff(new=value))
            for exclusive_hash, (key, value) in data2_exclusive_items.items()
            if exclusive_hash not in already_data2_hashes
        )
        if self.sorting_function is not None:
            output_copy:dict[str|D.Diff,d|D.Diff] = cast(Any, type(output)())
            output_copy.update((key, value) for key, value in sorted(output.items(), key=self.sorting_function))
            output = output_copy
        return output, has_changes, exceptions
