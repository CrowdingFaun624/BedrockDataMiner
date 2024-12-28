from types import EllipsisType
from typing import (TYPE_CHECKING, Any, Callable, Mapping, MutableMapping,
                    Union, cast)

import Component.Types as Types
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.ObjectStructure as ObjectStructure
import Structure.PrimitiveStructure as PrimitiveStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureSet as StructureSet
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate

class AbstractMappingStructure[d](ObjectStructure.ObjectStructure[MutableMapping[str, d]]):
    """
    Abstract class of dict-using Structures.
    In subclasses, must provide methods `iter_structures`, `check_type`,
    `get_structure`, `choose_structure`, `get_tag_paths`,
    `get_referenced_files`, `normalize`, and `get_max_similarity_descendent_depth`.
    """

    __slots__ = (
        "detect_key_moves",
        "key_structure",
        "key_weight",
        "max_similarity_ancestor_depth",
        "max_key_similarity_descendent_depth",
        "min_key_similarity_threshold",
        "min_value_similarity_threshold",
        "normalizer",
        "post_normalizer",
        "required_keys",
        "sorting_function",
        "value_weight",
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
        self.required_keys:list[str]|None = None

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

    def choose_structure(self, key:str|D.Diff[str], value:d|D.Diff[d]) -> tuple[StructureSet.StructureSet[d], list[Trace.ErrorTrace]]: ...

    def check_all_types(self, data:MutableMapping[str,d], environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        '''Recursively checks if the types are correct. Should not be given data containing Diffs.'''
        output:list[Trace.ErrorTrace] = []
        for key, value in data.items():
            if (check_type_output := self.check_type(key, value)) is not None:
                output.append(check_type_output)
                continue

            structure, new_exceptions = self.get_structure(key, value)
            output.extend(exception.add(self.name, key) for exception in new_exceptions)
            if structure is not None:
                output.extend(exception.add(self.name, key) for exception in structure.check_all_types(value, environment))
        assert self.required_keys is not None
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

    def get_similarity(self, data1: MutableMapping[str|D.Diff[str], d|D.Diff[d]], data2: MutableMapping[str, d], depth:int, max_depth:int|None, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace], branch:int) -> float:
        if (max_depth is not None and depth > max_depth) or (self.max_similarity_ancestor_depth is not None and depth > self.max_similarity_ancestor_depth):
            if branch == 0:
                return float(data1 == data2)
            else:
                return float(Structure.get_data_at_branch(data1, branch) == data2)
        data1_hashes:dict[int,tuple[str,d]] = {Types.hash_data((key_last:=D.last_value(key), value_last:=D.last_value(value))): (key_last, value_last) for key, value in data1.items()}
        data2_hashes:dict[int,tuple[str,d]] = {Types.hash_data((key, value)): (key, value) for key, value in data2.items()}

        data1_keys = {D.last_value(key) for key in data1.keys()}
        same_keys = data1_keys & data2.keys() # keys present in both old and new data.
        same_hashes = data1_hashes.keys() & data2_hashes.keys()
        data1_exclusive_items = {exclusive_hash: data1_hashes[exclusive_hash] for exclusive_hash in data1_hashes.keys() - data2_hashes.keys()}
        data2_exclusive_items = {exclusive_hash: data2_hashes[exclusive_hash] for exclusive_hash in data2_hashes.keys() - data1_hashes.keys()}

        similarity_count = sum(self.get_key_weight(*data1_hashes[hash], exceptions) for hash in same_hashes)
        total_weight = sum(self.get_key_weight(key_last:=D.last_value(key), None, exceptions) for key in data1_keys | data2.keys())
        if len(data1_exclusive_items) > 0 and len(data2_exclusive_items) > 0 and total_weight != 0:
            already_data1_hashes:set[int] = set() # items of data1_hashes that have already been picked.
            already_data2_hashes:set[int] = set() # items of data2_hashes that have already been picked.
            for hash1, hash2, key_similarity, value_similarity, key1, key2 in self.get_similarities_list(data1_exclusive_items, data2_exclusive_items, same_keys, depth, max_depth, environment, exceptions, branch, True):
                if hash1 in already_data1_hashes or hash2 in already_data2_hashes or not self.allow_key_move(key1, D.last_value(data1[key1]), key2, data2[key2], exceptions):
                    if len(already_data1_hashes) == len(data1_exclusive_items) or len(already_data2_hashes) == len(data2_exclusive_items):
                        break
                    continue
                already_data1_hashes.add(hash1)
                already_data2_hashes.add(hash2)
                similarity_count += ((self.get_key_weight(*data1_hashes[hash1], exceptions) + self.get_key_weight(*data2_hashes[hash2], exceptions))) * ((key_similarity * self.key_weight + value_similarity * self.value_weight)) / (2 * (self.key_weight + self.value_weight))
        similarity = similarity_count / total_weight if total_weight != 0 else 1.0
        if similarity < 0.0 or similarity > 1.0:
            exceptions.append(Trace.ErrorTrace(Exceptions.InvalidSimilarityError(self, similarity, data1, data2), self.name, None, (data1, data2)))
        return similarity

    def get_key_similarity(self, key1:str, key2:str, depth:int, max_depth:int|None|EllipsisType, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace], branch:int) -> float:
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
            return self.key_structure.get_similarity(key1, key2, depth + 1, max_depth, environment, exceptions, branch)
        else:
            return 0.0

    def get_value_similarity(self, key1:str, value1:d, key2:str, value2:d, depth:int, max_depth:int|None|EllipsisType, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace], branch:int) -> float:
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
            output = structure1.get_similarity(value1, value2, depth + 1, max_depth, environment, exceptions, branch)
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

    def get_key_weight(self, key:str, value:d|None, exceptions:list[Trace.ErrorTrace]) -> int:
        '''
        Returns the weight that the key has in similarity calculations.
        '''
        return 1

    def get_similarities_list(
        self,
        data1_exclusive_items:Mapping[int,tuple[str|D.Diff[str],d|D.Diff[d]]],
        data2_exclusive_items:Mapping[int,tuple[str,d]],
        same_keys:set[str],
        depth:int,
        max_depth:int|None|EllipsisType,
        environment:StructureEnvironment.ComparisonEnvironment,
        exceptions:list[Trace.ErrorTrace],
        branch:int,
        care_about_similarity:bool
    ) -> list[tuple[int,int,float,float,str,str]]:
        keys1_hashes:dict[str,tuple[int,d]] = {D.last_value(key1): (hash1, D.last_value(value1)) for hash1, (key1, value1) in data1_exclusive_items.items()}
        keys2_hashes:dict[str,tuple[int,d]] = {key2: (hash2, value2) for hash2, (key2, value2) in data2_exclusive_items.items()}
        unweighted_keys = self.get_unweighted_keys()
        same_keys_list:list[tuple[int, int, float, float, str, str]] = [
            (
                keys1_hashes[key][0],
                keys2_hashes[key][0],
                1.0,
                (self.get_value_similarity(key, D.last_value(keys1_hashes[key][1]), key, keys2_hashes[key][1], depth, max_depth, environment, exceptions, branch) if (care_about_similarity or key not in unweighted_keys) else 1.0),
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
                (hash1, hash2, key_similarity, value_similarity, D.last_value(key1), key2)
                # The only thing that matters here is the latest item of any differences.
                # Combining of differences is not the job of this function.
                for hash1, (key1, value1) in data1_exclusive_items.items()
                if key1 not in same_keys and key1 not in unweighted_keys
                for hash2, (key2, value2) in data2_exclusive_items.items()
                if key2 not in same_keys and key2 not in unweighted_keys and self.allow_key_move(D.last_value(key1), D.last_value(value1), key2, value2, exceptions)
                # key1 cannot equal key2
                if (key_similarity := self.get_key_similarity(D.last_value(key1), key2, depth, max_depth, environment, exceptions, branch)) >= self.min_key_similarity_threshold
                if (value_similarity := self.get_value_similarity(D.last_value(key1), D.last_value(value1), key2, value2, depth, max_depth, environment, exceptions, branch)) > self.min_value_similarity_threshold
            ]
            output = same_keys_list
            output.extend(similarities_list)
        else:
            output = same_keys_list
        # sort by weighted similarities using the thresholds.
        output.sort(key=lambda item: ((item[2] * self.key_weight + item[3] * self.value_weight) / (self.key_weight + self.value_weight), item[4], item[5]), reverse=True)
        return output

    def compare(
            self,
            data1:MutableMapping[str|D.Diff[str],d|D.Diff[d]],
            data2:MutableMapping[str,d],
            environment:StructureEnvironment.ComparisonEnvironment,
            branch:int,
            branches:int,
        ) -> tuple[MutableMapping[str|D.Diff[str],d|D.Diff[d]],bool,list[Trace.ErrorTrace]]:

        if not environment.is_multi_diff and (data1 is data2 or data1 == data2):
            return data1, False, []
        exceptions:list[Trace.ErrorTrace] = []

        data1_hashes:dict[int,tuple[str|D.Diff[str],d|D.Diff[d]]] = {Types.hash_data((D.last_value(key), D.last_value(value))): (key, value) for key, value in data1.items()}
        data2_hashes:dict[int,tuple[str,d]] = {Types.hash_data((key, value)): (key, value) for key, value in data2.items()}

        same_keys = {D.last_value(key) for key in data1.keys()} & data2.keys() # keys that existed both before and after.
        same_hashes = [hash for hash in data1_hashes.keys() if hash in data2_hashes] # retain order
        data1_exclusive_items = {exclusive_hash: data1_hashes[exclusive_hash] for exclusive_hash in data1_hashes if exclusive_hash not in data2_hashes}
        data2_exclusive_items = {exclusive_hash: data2_hashes[exclusive_hash] for exclusive_hash in data2_hashes if exclusive_hash not in data1_hashes}
        output:dict[str|D.Diff[str],d|D.Diff[d]] = cast(Any, type(data2)())
        has_changes = len(data1_exclusive_items) > 0 or len(data2_exclusive_items) > 0

        # unchanged items
        # or, more specifically, items that are unchanged between branch and branch+1
        for same_hash in same_hashes:
            key, value = data1_hashes[same_hash]
            if isinstance(key, D.Diff):
                key = key.extend(branch+1)
            if isinstance(value, D.Diff):
                value_diff = cast("D.Diff[d]", value)
                value = value_diff.extend(branch+1)
            elif TYPE_CHECKING: # I WILL HAVE my types be nice and nice. you can't stop me. haha.
                value = cast(d, value)
            output[key] = value

        # changed items
        already_data1_hashes:set[int] = set() # items of data1_hashes that have already been picked.
        already_data2_hashes:set[int] = set() # items of data2_hashes that have already been picked.
        if len(data1_exclusive_items) > 0 and len(data2_exclusive_items) > 0:
            for hash1, hash2, _, _, _, _ in self.get_similarities_list(data1_exclusive_items, data2_exclusive_items, same_keys, 1, ..., environment, exceptions, branch, False):

                if hash1 in already_data1_hashes or hash2 in already_data2_hashes:
                    if len(already_data1_hashes) == len(data1_exclusive_items) or len(already_data2_hashes) == len(data2_exclusive_items):
                        break
                    continue # if either side is already involved in a change, it's unneeded.
                already_data1_hashes.add(hash1)
                already_data2_hashes.add(hash2)
                key1, value1 = data1_exclusive_items[hash1]
                key2, value2 = data2_exclusive_items[hash2]
                structure1, new_exceptions = self.get_structure(D.last_value(key1), D.last_value(value1))
                exceptions.extend(exception.add(self.name, key1) for exception in new_exceptions)
                structure2, new_exceptions = self.get_structure(key2, value2)
                exceptions.extend(exception.add(self.name, key2) for exception in new_exceptions)

                if key1 == key2:
                    key_compare_output = key1
                elif self.key_structure is None or isinstance(self.key_structure, PrimitiveStructure.PrimitiveStructure):
                    # PrimitiveStructure always returns a Diff as its output if the data are different.
                    if isinstance(key1, D.Diff):
                        if key1.last_value == key2:
                            # If they're equal, it can just be extended.
                            key_compare_output = key1.extend(branch+1)
                        else:
                            key_compare_output = key1.append(branch+1, key2)
                    else:
                        key_compare_output = D.Diff(branches, {tuple(range(0,branch+1)): key1, (branch+1,): key2})
                elif isinstance(key1, D.Diff):
                    comparison, _, new_exceptions = self.key_structure.compare(key1.last_value, key2, environment, branch, branches)
                    exceptions.extend(exception.add(self.name, key2) for exception in new_exceptions)
                    key_compare_output = key1.with_last_as(branch+1, comparison)
                else:
                    key_compare_output, _, new_exceptions = self.key_structure.compare(key1, key2, environment, branch, branches)
                    exceptions.extend(exception.add(self.name, key2) for exception in new_exceptions)

                if value1 is value2 or value1 == value2:
                    # value1 cannot equal value2 when value1 is a Diff.
                    value_compare_output = value2
                elif structure1 is not structure2 or structure1 is None:
                    if isinstance(value1, D.Diff):
                        value1_diff = cast("D.Diff[d]", value1)
                        if value1_diff.last_value == value2:
                            value_compare_output = value1.extend(branch+1)
                        else:
                            value_compare_output = value1_diff.append(branch+1, value2)
                    else:
                        value1_object = cast(d, value1)
                        value_compare_output = D.Diff(branches, {tuple(range(0,branch+1)): value1_object, (branch+1,): value2})
                elif isinstance(value1, D.Diff):
                    value1_diff = cast("D.Diff[d]", value1)
                    comparison, _, new_exceptions = structure1.compare(value1_diff.last_value, value2, environment, branch, branches)
                    exceptions.extend(exception.add(self.name, key2) for exception in new_exceptions)
                    value_compare_output = value1_diff.with_last_as(branch+1, comparison)
                else:
                    value1_object = cast(d, value1)
                    value_compare_output, _, new_exceptions = structure1.compare(value1_object, value2, environment, branch, branches)
                    exceptions.extend(exception.add(self.name, key2) for exception in new_exceptions)

                output[key_compare_output] = value_compare_output

        # removed items
        output.update(
            (
                key if isinstance(key, D.Diff) else D.Diff(branches, {tuple(range(0,branch+1)): key}),
                value if isinstance(value, D.Diff) else D.Diff(branches, {tuple(range(0,branch+1)): value}),
            )
            for exclusive_hash, (key, value) in data1_exclusive_items.items()
            if exclusive_hash not in already_data1_hashes
        )
        # added items
        output.update(
            (
                # neither key1 nor key2 can be Diffs.
                D.Diff(branches, {(branch+1,): key}),
                D.Diff(branches, {(branch+1,): value}),
            )
            for exclusive_hash, (key, value) in data2_exclusive_items.items()
            if exclusive_hash not in already_data2_hashes
        )
        if self.sorting_function is not None:
            output_copy = type(output)()
            output_copy.update((key, value) for key, value in sorted(output.items(), key=self.sorting_function))
            output = output_copy
        return output, has_changes, exceptions
