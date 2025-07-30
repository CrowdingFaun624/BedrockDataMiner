from itertools import count, takewhile
from types import EllipsisType
from typing import TYPE_CHECKING, Hashable, Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.IterableContainer import ICon, IDon, idon_from_list
from Structure.IterableStructure import IterableStructure
from Structure.SimilarityCache import SimilarityCache
from Structure.Structure import Structure
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Structure.Uses import NonEmptyUse, Region, StructureUse, TypeUse, Use
from Utilities.Exceptions import SequenceTooLongError
from Utilities.Trace import Trace

if TYPE_CHECKING:
    import numpy

NONE = 0 # .
HORIZONTAL = 1 # -
VERTICAL = 2 # |
DIAGONAL_NO_CHANGE = 3 # *
DIAGONAL_SUBSTITUTION_KEY = 4 # &
DIAGONAL_SUBSTITUTION_VALUE = 5 # ^
DIAGONAL_SUBSTITUTION_BOTH = 6 # \

class SequenceStructure[K:Hashable, V, D, KBO, KCO, VBO, VCO, BO, CO](IterableStructure[K, V, D, KBO, KCO, VBO, VCO, BO, CO]):

    KEY_WEIGHT = 2
    VALUE_WEIGHT = 8

    __slots__ = (
        "addition_cost",
        "deletion_cost",
        "key_structure",
        "key_weight",
        "max_square_length",
        "similarity_cache",
        "substitution_cost",
        "value_structure",
        "value_types",
        "value_weight",
    )

    def link_sequence_structure(
        self,
        addition_cost:float,
        deletion_cost:float,
        key_structure:Structure[K, Con[K], Don[K], Don[K]|Diff[Don[K]], KBO, KCO]|None,
        key_weight:int,
        max_square_length:int,
        substitution_cost:float,
        value_structure:Structure[V, Con[V], Don[V], Don[V]|Diff[Don[V]], VBO, VCO]|None,
        value_types:tuple[type,...],
        value_weight:int,
    ) -> None:
        self.addition_cost = addition_cost
        self.deletion_cost = deletion_cost
        self.key_structure = key_structure
        self.key_weight = key_weight
        self.max_square_length = max_square_length
        self.substitution_cost = substitution_cost
        self.value_structure = value_structure
        self.value_types = value_types
        self.value_weight = value_weight

        self.similarity_cache:SimilarityCache[Con[D]] = SimilarityCache()

    def get_similarity_caches(self) -> Sequence[SimilarityCache]:
        return (self.similarity_cache,)

    def get_key_structure(self, key: K, value: V, trace: Trace, environment: PrinterEnvironment) -> Structure[K, Con[K], Don[K], Don[K]|Diff[Don[K]], KBO, KCO]|None:
        return self.key_structure

    def get_value_structure(self, key: K, value: V, trace: Trace, environment: PrinterEnvironment) -> Structure[V, Con[V], Don[V], Don[V]|Diff[Don[V]], VBO, VCO]|None:
        return self.value_structure

    def get_value_types(self, key: K, value: V, trace: Trace, environment: PrinterEnvironment) -> tuple[type, ...]:
        return self.value_types

    def iter_structures(self) -> Sequence[Structure]:
        output:list[Structure] = []
        if self.key_structure is not None:
            output.append(self.key_structure)
        if self.value_structure is not None:
            output.append(self.value_structure)
        return output

    def get_all_uses(self, memo: set[Structure], parent_use:Use|None,) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        output:OrderedSet[Use] = OrderedSet(())
        output.update(super().get_all_uses(memo, parent_use))
        non_empty_use = NonEmptyUse(self, None, StructureUse(self, None, parent_use))
        if self.key_structure is not None:
            output.update(self.key_structure.get_all_uses(memo, non_empty_use if self.key_structure.is_inline else None))
        if self.value_structure is not None:
            output.update(self.value_structure.get_all_uses(memo, non_empty_use if self.value_structure.is_inline else None))
        for value_type in self.value_types:
            output.add(TypeUse(value_type, Region.value_types, non_empty_use, None))
        return output

    def compare(
        self,
        datas:tuple[tuple[int, ICon[Con[K], Con[V], D]], ...],
        trace: Trace,
        environment:ComparisonEnvironment
    ) -> tuple[IDon[Diff[Don[K]], Diff[Don[V]], D, Con[K], Con[V]] | EllipsisType, bool, bool]:
        with trace.enter(self, self.trace_name, datas):
            any_changes:bool = False
            cumulative_items:list[tuple[list[tuple[list[int], Con[K]]], list[tuple[list[int], Con[V]]]]] = []
            first_branch = datas[0][0]
            for branch2, data2 in datas:
                if branch2 != first_branch:
                    data1_list:list[tuple[tuple[int, Con[K]], tuple[int, Con[V]]]] = [((key[-1][0][-1], key[-1][1]), (value[-1][0][-1], value[-1][1])) for key, value in cumulative_items]
                    data2_list = list(data2.items())
                    prefix_len, suffix_len = self.get_prefix_suffix_len(data1_list, data2_list)
                    if (len(data1_list) - prefix_len - suffix_len) * (len(data2_list) - prefix_len - suffix_len) > self.max_square_length:
                        raise SequenceTooLongError(self, len(data1_list), len(data2_list))
                    distances, path = self.get_distances(data1_list, data2_list, branch2, prefix_len, suffix_len, trace, environment)
                    cumulative_items, has_changes = self.retrace_path(cumulative_items, data2_list, branch2, prefix_len, suffix_len, path)
                    any_changes = any_changes or has_changes
                else:
                    cumulative_items.extend(([([branch2], key)], [([branch2], value)]) for key, value in data2.items())
            assembled_output = self.assemble_output(cumulative_items, trace, environment)
            return idon_from_list(assembled_output, {branch: data for branch, data in datas}), any_changes, any_changes
        return ..., False, False

    def get_similarity(self, data1: ICon[Con[K], Con[V], D], data2: ICon[Con[K], Con[V], D], branch1: int, branch2: int, trace: Trace, environment: ComparisonEnvironment) -> tuple[float, bool]:
        with trace.enter(self, self.trace_name, (data1, data2)):
            if (output := self.similarity_cache.get(data1, data2, environment1 := environment[branch1], environment2 := environment[branch2])) is not None:
                return output
            data1_list = [((branch1, key), (branch1, value)) for key, value in data1.items()]
            data2_list = list(data2.items())
            prefix_len, suffix_len = self.get_prefix_suffix_len(data1_list, data2_list)
            if (len(data1_list) - prefix_len - suffix_len) * (len(data2_list) - prefix_len - suffix_len) > self.max_square_length:
                raise SequenceTooLongError(self, len(data1_list), len(data2_list))
            distances, path = self.get_distances(data1_list, data2_list, branch2, prefix_len, suffix_len, trace, environment)
            levenshtein_distance = float(distances[len(data2_list) - prefix_len - suffix_len, len(data1_list) - prefix_len - suffix_len])
            max_length = max(len(data1_list), len(data2_list))
            output = (1 - (levenshtein_distance / max_length), self.path_implies_identicalness(len(data1_list), len(data2_list), prefix_len, suffix_len, path))
            return self.similarity_cache.set(output, data1, data2, environment1, environment2)
        return 0.0, False

    def get_prefix_suffix_len(self, data1:list[tuple[tuple[int, Con[K]], tuple[int, Con[V]]]], data2:list[tuple[Con[K], Con[V]]]) -> tuple[int, int]:
        prefix_len = sum(1 for i in takewhile(lambda items: items[0][0][1] == items[1][0] and items[0][1][1] == items[1][1], zip(data1, data2)))
        # number of items at start that are the same
        shorter_length = min(len(data1), len(data2))
        suffix_len = sum(1 for i in takewhile(lambda items: items[0] < shorter_length - prefix_len and items[1][0][1] == items[2][0] and items[1][1][1] == items[2][1], zip(count(), reversed(data1), reversed(data2))))
        # number of items at end that are the same unless that line is included in prefix_len.
        return prefix_len, suffix_len

    def get_distances(
        self,
        data1:list[tuple[tuple[int, Con[K]], tuple[int, Con[V]]]],
        data2:list[tuple[Con[K], Con[V]]],
        branch2:int,
        prefix_len:int,
        suffix_len:int,
        trace:Trace,
        environment:ComparisonEnvironment,
    ) -> tuple["numpy.ndarray[tuple[int, int], numpy.dtype[numpy.float32]]", "numpy.ndarray[tuple[int, int], numpy.dtype[numpy.int8]]"]:
        import numpy
        distances = numpy.zeros((len(data2) + 1 - prefix_len - suffix_len, len(data1) + 1 - prefix_len - suffix_len), numpy.float32)
        path = numpy.zeros((len(data2) + 1 - prefix_len - suffix_len, len(data1) + 1 - prefix_len - suffix_len), numpy.int8)
        for x in range(1, len(data1) + 1 - prefix_len - suffix_len):
            distances[0, x] = x * self.deletion_cost
            path[0, x] = HORIZONTAL
        for y in range(1, len(data2) + 1 - prefix_len - suffix_len):
            distances[y, 0] = y * self.addition_cost
            path[y, 0] = VERTICAL
        for y in range(len(data2) - prefix_len - suffix_len):
            for x in range(len(data1) - prefix_len - suffix_len):
                distances[y + 1, x + 1], path[y + 1, x + 1] = self.get_cost(x, y, prefix_len, branch2, data1, data2, distances, trace, environment)
        return distances, path

    def get_cost(
        self,
        x:int,
        y:int,
        prefix_len:int,
        branch2:int,
        data1:list[tuple[tuple[int, Con[K]], tuple[int, Con[V]]]],
        data2:list[tuple[Con[K], Con[V]]],
        distances:"numpy.ndarray[tuple[int, int], numpy.dtype[numpy.float32]]",
        trace:Trace,
        environment:ComparisonEnvironment,
    ) -> tuple[float, int]: # cost, path
        deletion_cost:float = distances[y + 1, x] + self.deletion_cost
        addition_cost:float = distances[y, x + 1] + self.addition_cost
        (key_branch1, key1), (value_branch1, value1) = data1[x + prefix_len]
        key2, value2 = data2[y + prefix_len]
        key_similarity, keys_identical = self.get_key_similarity(key1, key2, value1, value2, key_branch1, branch2, trace, environment)
        value_similarity, values_identical = self.get_value_similarity(key1, key2, value1, value2, value_branch1, branch2, trace, environment)
        substitution_cost = distances[y, x] + self.substitution_cost * (1 - (key_similarity * self.key_weight + value_similarity * self.value_weight) / (self.key_weight + self.value_weight))
        if keys_identical and values_identical:
            return substitution_cost, DIAGONAL_NO_CHANGE
        elif substitution_cost < addition_cost and substitution_cost < deletion_cost:
            if values_identical:
                return substitution_cost, DIAGONAL_SUBSTITUTION_KEY
            elif keys_identical:
                return substitution_cost, DIAGONAL_SUBSTITUTION_VALUE
            else:
                return substitution_cost, DIAGONAL_SUBSTITUTION_BOTH
        elif addition_cost < substitution_cost and addition_cost < deletion_cost:
            return addition_cost, VERTICAL
        else:
            return deletion_cost, HORIZONTAL

    def retrace_path(
        self,
        cumulative_items:list[tuple[list[tuple[list[int], Con[K]]], list[tuple[list[int], Con[V]]]]],
        data2:list[tuple[Con[K], Con[V]]],
        branch2:int,
        prefix_len:int,
        suffix_len:int,
        path:"numpy.ndarray[tuple[int, int], numpy.dtype[numpy.int8]]",
    ) -> tuple[list[tuple[list[tuple[list[int], Con[K]]], list[tuple[list[int], Con[V]]]]], bool]:
        any_changes:bool = False
        x = len(cumulative_items) - prefix_len - suffix_len # data1 index
        y = len(data2) - prefix_len - suffix_len # data2 index
        output:list[tuple[list[tuple[list[int], Con[K]]], list[tuple[list[int], Con[V]]]]] = []
        # output is the same structure as `cumulative_items`. By the end of this algorithm, it should contain all information
        # from `cumulative_items` and `data2`.
        if suffix_len != 0:
            for item in cumulative_items[:len(cumulative_items) - suffix_len - 1:-1]: # add in the suffix of `cumulative_items` first because it'll be reversed later.
                item[0][-1][0].append(branch2)
                item[1][-1][0].append(branch2)
                output.append(item)
        while x != 0 or y != 0:
            path_item = int(path[y, x])
            if path_item == DIAGONAL_NO_CHANGE:
                x -= 1; y -= 1
                item = cumulative_items[prefix_len + x]
                output.append(item)
                item[0][-1][0].append(branch2) # add key branch
                item[1][-1][0].append(branch2) # add value branch
                # data2[y] is forgotten because the key and value are equal to the key and value in item.
            elif path_item == DIAGONAL_SUBSTITUTION_KEY:
                any_changes = True
                x -= 1; y -= 1
                item = cumulative_items[prefix_len + x]
                output.append(item)
                item[0].append(([branch2], data2[prefix_len + y][0]))
                item[1][-1][0].append(branch2) # add value branch
                # data2[y][1] is forgotten because the value is equal to the value in item.
            elif path_item == DIAGONAL_SUBSTITUTION_VALUE:
                any_changes = True
                x -= 1; y -= 1
                item = cumulative_items[prefix_len + x]
                output.append(item)
                item[1].append(([branch2], data2[prefix_len + y][1]))
                item[0][-1][0].append(branch2) # add key branch
                # data2[y][0] is forgotten because the key is equal to the key in item.
            elif path_item == DIAGONAL_SUBSTITUTION_BOTH:
                any_changes = True
                x -= 1; y -= 1
                item = cumulative_items[prefix_len + x]
                output.append(item)
                item[0].append(([branch2], data2[prefix_len + y][0]))
                item[1].append(([branch2], data2[prefix_len + y][1]))
            elif path_item == VERTICAL: # addition
                any_changes = True
                y -= 1
                output.append(([([branch2], data2[prefix_len + y][0])], [([branch2], data2[prefix_len + y][1])]))
            else: # path_item == HORIZONTAL: # removal
                any_changes = True
                x -= 1
                output.append(cumulative_items[prefix_len + x])
                # Since y did not change, data2[y] cannot be accessed, lest it
                # be duplicated somewhere else. Because the old
                # `cumulative_items` will be replaced by `output`, we will add
                # this item to `output`.
        if prefix_len != 0:
            for item in cumulative_items[prefix_len-1::-1]: # add in the suffix of `cumulative_items` first because it'll be reversed later.
                item[0][-1][0].append(branch2)
                item[1][-1][0].append(branch2)
                output.append(item)
        output.reverse() # the above process starts at the end of the sequence and goes backward.
        return output, any_changes

    def path_implies_identicalness(
        self,
        data1_length:int,
        data2_length:int,
        prefix_len:int,
        suffix_len:int,
        path:"numpy.ndarray[tuple[int, int], numpy.dtype[numpy.int8]]",
    ) -> bool:
        '''
        Returns if all items in the path are DIAGONAL_NO_CHANGE.
        '''
        initial_x = data1_length - prefix_len - suffix_len
        initial_y = data2_length - prefix_len - suffix_len
        return data1_length == data2_length and all(path[initial_y - pos, initial_x - pos] == DIAGONAL_NO_CHANGE or pos == data1_length - prefix_len - suffix_len for pos in range(path.shape[0]))

    def render_full_path(self, path:"numpy.ndarray[tuple[int, int], numpy.dtype[numpy.int8]]") -> None:
        '''
        Prints a representation of `path` for debugging purposes.
        '''
        CHARACTERS = ".-|*&^\\"
        lines:list[str] = []
        y_size, x_size = path.shape
        for y in range(y_size):
            line:list[str] = []
            for x in range(x_size):
                line.append(CHARACTERS[path[y, x]])
            lines.append("".join(line))
        output = "\n".join(lines)
        print(output)
