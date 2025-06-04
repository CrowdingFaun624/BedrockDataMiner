from types import EllipsisType
from typing import Callable, Container, Hashable, Iterable, Mapping, Sequence

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.IterableContainer import ICon, IDon, idon_from_list
from Structure.IterableStructure import IterableStructure
from Structure.SimilarityCache import SimilarityCache
from Structure.StructureEnvironment import ComparisonEnvironment
from Structure.StructureInfo import StructureInfo
from Utilities.Trace import Trace


def special_enumerate[A](iterable:Sequence[A], start_index:int) -> Iterable[tuple[int,A]]:
    '''
    Returns results similar to enumerate, except that it grows both left and right from `start_index`.
    :iterable: The values to yield.
    :start_index: The index to start from.
    '''
    length = len(iterable)
    if length == 0:
        return
    elif start_index <= 0:
        yield from enumerate(iterable)
    elif start_index >= length:
        yield from ((length - index - 1, item) for index, item in enumerate(reversed(iterable)))
    else:
        left_iterator = enumerate(iterable[start_index - 1::-1]) # start_index - index - 1
        right_iterator = enumerate(iterable[start_index::], start_index)
        right_length = length - start_index
        left_length = start_index
        for i in range(min(right_length, left_length)):
            yield next(right_iterator)
            yield (start_index - (left_item := next(left_iterator))[0] - 1, left_item[1])
        if right_length > left_length: # right_iterator still has more items to yield.
            yield from right_iterator
        elif right_length != left_length: # left_length > right_length; left_iterator still has more items to yield.
            yield from ((start_index - index - 1, item) for index, item in left_iterator)
        else: # right_iterator and left_iterator have equal length; no more items to yield.
            return

class MappingStructure[K:Hashable, V, D, KBO, KCO, VBO, VCO, BO, CO](IterableStructure[K, V, D, KBO, KCO, VBO, VCO, BO, CO]):

    MIN_KEY_SIMILARITY_THRESHOLD = 0.5
    MIN_VALUE_SIMILARITY_THRESHOLD = 0.5
    KEY_WEIGHT = 1
    VALUE_WEIGHT = 1

    __slots__ = (
        "allow_same_key_optimization",
        "key_moves_ever_allowed",
        "min_key_similarity_threshold",
        "min_value_similarity_threshold",
        "similarity_cache",
    )

    def link_mapping_structure(
        self,
        min_key_similarity_threshold:float,
        min_value_similarity_threshold:float,
    ) -> None:
        self.allow_same_key_optimization = True
        self.key_moves_ever_allowed = True
        '''
        Can only be False if `allow_key_move` returns False no matter its inputs.
        '''
        self.min_key_similarity_threshold = min_key_similarity_threshold
        self.min_value_similarity_threshold = min_value_similarity_threshold

        self.similarity_cache:SimilarityCache[Con[D]] = SimilarityCache()

    def clear_similarity_cache(self, keep: Container[StructureInfo]) -> None:
        self.similarity_cache.clear(keep)

    def allow_key_move(self, key1:Con[K], key2:Con[K], value1:Con[V], value2:Con[V], branch1:int, branch2:int, trace:Trace, environment:ComparisonEnvironment) -> bool:
        return True

    def get_similarity_weight(self, key:Con[K], value:Con[V], trace:Trace, environment:ComparisonEnvironment) -> int:
        '''
        Returns the weight of the key-value pair in similarity calculations.
        '''
        return 1

    def get_key_weight(self, key:Con[K], value:Con[V], trace:Trace, environment:ComparisonEnvironment) -> int:
        return 1

    def get_value_weight(self, key:Con[K], value:Con[V], trace:Trace, environment:ComparisonEnvironment) -> int:
        return 1

    def compare(
        self,
        datas: tuple[tuple[int, ICon[Con[K], Con[V], D]], ...],
        trace: Trace,
        environment: ComparisonEnvironment,
    ) -> tuple[IDon[Diff[Don[K]], Diff[Don[V]], D, Con[K], Con[V]]|EllipsisType, bool, bool]:
        with trace.enter(self, self.name, datas):
            SELECTION_FUNCTION = lambda key: (key[-1][0][-1], key[-1][1])
            any_changes:bool = False
            # first set is keys in older data and not in newer data; second set is keys in newer data and not in older data.
            cumulative_items:list[tuple[list[tuple[list[int], Con[K]]], list[tuple[list[int], Con[V]]]]] = [] # basically the output
            cumulative_mapping:dict[Con[K], tuple[int, int]] = {} # maps keys to index in cumulative_items and branch. Items are overwritten frequently.
            previous_length:int|EllipsisType = ...
            first_branch = datas[0][0]
            for branch, data in datas:
                similarities:list[tuple[float, int, int, bool, bool, int, int, int, Con[K], Con[V]]] = []
                current_length:int = 0
                if branch != first_branch:
                    unassigned_indices:dict[int,tuple[Con[K],Con[V]]] = {} # key-value pairs that were not similar to anything, and will become new additions.
                    for index, (key, value) in enumerate(data.items()):
                        with trace.enter_key(key, value):
                            current_length += 1
                            unassigned_indices[index] = (key, value)
                            similarities.extend(self.get_best_key_value_pair(key, value, index, branch, cumulative_items, cumulative_mapping, SELECTION_FUNCTION, SELECTION_FUNCTION, trace, environment))
                    if previous_length is not ... and previous_length != current_length:
                        any_changes = True # other methods of detecting changes do not account for removals.
                    similarities.sort(key=(lambda item: (3 - item[3] * 2 - item[4], 1 - item[0], item[2])) if self.allow_same_key_optimization else (lambda item: (1 - item[0], 3 - item[3] * 2 - item[4], item[2]))) # highest similarities are first
                    used_cumulative_indices:set[int] = set()
                    used_current_indices:set[int] = set()
                    for _, cumulative_index, current_index, keys_identical, values_identical, _, _, _, key, value in similarities:
                        if cumulative_index in used_cumulative_indices or current_index in used_current_indices:
                            continue
                        used_cumulative_indices.add(cumulative_index)
                        used_current_indices.add(current_index)
                        del unassigned_indices[current_index]
                        cumulative_mapping[key] = (cumulative_index, branch) # overwriting of previous values is intentional behavior.
                        if keys_identical:
                            cumulative_items[cumulative_index][0][-1][0].append(branch)
                        else:
                            any_changes = True
                            cumulative_items[cumulative_index][0].append(([branch], key))
                        if values_identical:
                            cumulative_items[cumulative_index][1][-1][0].append(branch)
                        else:
                            any_changes = True
                            cumulative_items[cumulative_index][1].append(([branch], value))
                    any_changes = any_changes or len(unassigned_indices) > 0
                    cumulative_mapping.update((key, (index, branch)) for index, (key, _) in enumerate(unassigned_indices.values(), len(cumulative_items)))
                    cumulative_items.extend(([([branch], key)], [([branch], value)]) for key, value in unassigned_indices.values())
                else: # branch == 0
                    cumulative_items.extend(([([0], key)], [([branch], value)]) for key, value in data.items())
                    cumulative_mapping.update((key, (index, 0)) for index, key in enumerate(data.keys()))
                    current_length = len(cumulative_items)
                previous_length = current_length
            assembled_output, any_internal_changes = self.assemble_output(cumulative_items, trace, environment)
            return idon_from_list(assembled_output, {branch: data for branch, data in datas}), any_changes, any_internal_changes
        return ..., False, False

    def get_similarity(self, data1: ICon[Con[K], Con[V], D], data2: ICon[Con[K], Con[V], D], branch1: int, branch2: int, trace: Trace, environment: ComparisonEnvironment) -> tuple[float, float]:
        with trace.enter(self, self.name, (data1, data2)):
            if (output := self.similarity_cache.get(data1, data2, structure_info1 := (environment[branch1].structure_info), structure_info2 := (environment[branch2].structure_info))) is not None:
                return output
            similarities:list[tuple[float, int, int, bool, bool, int, int, int, Con[K], Con[V]]] = []
            data1_list = list(data1.items())
            data1_mapping = {key: (index, branch1) for index, (key, _) in enumerate(data1_list)}
            data2_length:int = 0
            for index2, (key2, value2) in enumerate(data2.items()):
                data2_length += 1
                similarities.extend(self.get_best_key_value_pair(key2, value2, index2, branch2, data1_list, data1_mapping, lambda key: (branch1, key), lambda value: (branch1, value), trace, environment))
            similarities.sort(key=(lambda item: (3 - item[3] * 2 - item[4], 1 - item[0], item[2])) if self.allow_same_key_optimization else (lambda item: (1 - item[0], 3 - item[3] * 2 - item[4], item[2])))
            used_indices1:set[int] = set()
            used_indices2:set[int] = set()
            cumulative_similarity:float = 0.0
            identical = len(similarities) > 0 or (len(data1_list) == 0 and data2_length == 0) # if similarities is empty, the objects likely have no common elements. If both data are empty, then they are identical.
            maximum_similarity = sum(self.get_similarity_weight(key, value, trace, environment) for key, value in data1.items()) + sum(self.get_similarity_weight(key, value, trace, environment) for key, value in data2.items())
            for similarity, index1, index2, keys_identical, values_identical, key_weight, value_weight, similarity_weight, key2, value2 in similarities:
                if index1 in used_indices1 or index2 in used_indices2:
                    continue
                used_indices1.add(index1)
                used_indices2.add(index2)
                cumulative_similarity += similarity * similarity_weight
                identical = identical and (keys_identical or key_weight == 0) and (values_identical or value_weight == 0)
            output = (cumulative_similarity / maximum_similarity) if maximum_similarity != 0 else 1.0, identical and cumulative_similarity == maximum_similarity
            return self.similarity_cache.set(output, data1, data2, structure_info1, structure_info2)
        return 0.0, False

    def get_best_key_value_pair[A, B](
        self,
        key2:Con[K],
        value2:Con[V],
        index:int,
        branch2:int,
        key_value_pairs:list[tuple[A, B]],
        key_value_map:Mapping[Con[K], tuple[int, int]],
        key_function:Callable[[A], tuple[int, Con[K]]],
        value_function:Callable[[B], tuple[int, Con[V]]],
        trace:Trace,
        environment:ComparisonEnvironment,
    ) -> list[tuple[float, int, int, bool, bool, int, int, int, Con[K], Con[V]]]:
        '''
        :key2: The newest key.
        :value2: The newest value.
        :index: Index of the key-value pair `(key2, value2)` in its source.
        :branch2: Branch that `key2` and `value2` come from.
        :key_value_pairs: List of things that can get the branches, keys, and values of the older data.
        :key_value_map: Mapping of keys to its index in `key_value_pairs` from older data and the branch in the older data it appears in.
        :key_function: Function called on the first item of each item of `key_value_pairs`, returning its branch and key.
        :value_function: Function called on the second item of each item of `key_value_pairs`, returning its branch and value.
        :return: A list of similarity, index1, index2, key similarity, value similarity, key2, and value2.
        '''
        similarities:list[tuple[float, int, int, bool, bool, int, int, int, Con[K], Con[V]]] = []
        index_branch = key_value_map.get(key2)
        if (skip_same_key := index_branch is not None):
            # this block is for detecting when a key is the same to avoid the big loop below.
            # key1 == key2 in this block
            index_diff, key_branch = index_branch
            value_branch, value1 = value_function(key_value_pairs[index_diff][1])
            value_similarity, values_identical = self.get_value_similarity(key2, key2, value1, value2, value_branch, branch2, trace, environment)
            # allow all same-key things no matter how different their values are IF allow_same_key_optimization is true.
            if self.allow_same_key_optimization or value_similarity >= self.min_value_similarity_threshold and (1.0 != self.min_key_similarity_threshold or value_similarity != self.min_value_similarity_threshold):
                key_weight = self.get_key_weight(key2, value1, trace, environment) + self.get_key_weight(key2, value2, trace, environment)
                value_weight = self.get_value_weight(key2, value1, trace, environment) + self.get_value_weight(key2, value2, trace, environment)
                similarity_weight = self.get_similarity_weight(key2, value1, trace, environment) + self.get_similarity_weight(key2, value2, trace, environment)
                similarities.append((
                    (key_weight + value_similarity * value_weight) / (key_weight + value_weight),
                    index_diff, index, True, values_identical, key_weight, value_weight, similarity_weight, key2, value2,
                ))
            if values_identical or self.allow_same_key_optimization:
                return similarities
            # if the above block doesn't return, must search for key manually.
        if not self.key_moves_ever_allowed:
            # if the above process does not work, there is no key that gives key_similarity == 1.0.
            return []

        for index_diff, (key_object, value_object) in special_enumerate(key_value_pairs, index):
            key_branch, key1 = key_function(key_object)
            if skip_same_key and key1 == key2: # above if statement can sometimes duplicate the stuff in this for statement.
                continue
            value_branch, value1 = value_function(value_object)

            key_similarity, keys_identical = self.get_key_similarity(key1, key2, value1, value2, key_branch, branch2, trace, environment)
            if key_similarity < self.min_key_similarity_threshold:
                # may be skipped if any similarity does not reach the required threshold.
                continue
            value_similarity, values_identical = self.get_value_similarity(key1, key2, value1, value2, value_branch, branch2, trace, environment)
            if (value_similarity < self.min_value_similarity_threshold or (key_similarity == self.min_key_similarity_threshold and value_similarity == self.min_value_similarity_threshold)) and not (keys_identical and self.allow_same_key_optimization):
                continue
            if not keys_identical and not self.allow_key_move(key1, key2, value1, value2, key_branch, branch2, trace, environment) and not self.allow_same_key_optimization:
                # may be skipped if the keys are not the same and the key move is disallowed.
                continue

            # these technically are an average, but dividing by two doesn't change the end result anyways.
            key_weight = self.get_key_weight(key1, value1, trace, environment) + self.get_key_weight(key2, value2, trace, environment)
            value_weight = self.get_value_weight(key1, value1, trace, environment) + self.get_value_weight(key2, value2, trace, environment)
            similarity_weight = self.get_similarity_weight(key1, value1, trace, environment) + self.get_similarity_weight(key2, value2, trace, environment)
            similarities.append((
                (key_similarity * key_weight + value_similarity * value_weight) / (key_weight + value_weight),
                index_diff, index, keys_identical, values_identical, key_weight, value_weight, similarity_weight, key2, value2,
            ))
            if (keys_identical or key_weight == 0) and (values_identical or value_weight == 0 or (keys_identical and self.allow_same_key_optimization)):
                # cannot get anything better than this.
                break
        return similarities
