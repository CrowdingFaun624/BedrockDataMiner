from itertools import count, takewhile
from typing import Callable, Sequence, TypeVar

import numpy

import Structure.AbstractIterableStructure as AbstractIterableStructure
import Structure.Difference as D
import Structure.Hashing as Hashing
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

d = TypeVar("d")

NONE = 0
HORIZONTAL = 1
VERTICAL = 2
DIAGONAL_SUBSTITUTION = 3
DIAGONAL_NO_CHANGE = 4

class SequenceStructure(AbstractIterableStructure.AbstractIterableStructure[d]):
    '''
    Sequential data structure. Uses levenshtein distance for comparing.
    '''

    def __init__(
        self,
        name: str,
        addition_cost:float,
        deletion_cost:float,
        substitution_cost:float,
        max_similarity_descendent_depth:int|None,
        max_similarity_ancestor_depth:int|None,
        children_has_normalizer: bool,
        children_has_garbage_collection:bool,
    ) -> None:
        super().__init__(name, max_similarity_descendent_depth, max_similarity_ancestor_depth, children_has_normalizer, children_has_garbage_collection)

        self.addition_cost = addition_cost
        self.deletion_cost = deletion_cost
        self.substitution_cost = substitution_cost

    def get_similarity(self, data1: Sequence[d], data2: Sequence[d], depth:int, max_depth:int|None, environment: StructureEnvironment.ComparisonEnvironment, exceptions: list[Trace.ErrorTrace]) -> float:
        if (max_depth is not None and depth > max_depth) or (self.max_similarity_ancestor_depth is not None and depth > self.max_similarity_ancestor_depth):
            return float(data1 == data2)
        if len(data1) * len(data2) > 10_000_000:
            raise Exceptions.SequenceTooLongError(self, len(data1), len(data2))
        similarity_function = self.structure.get_similarity if self.structure is not None else lambda data1, data2, depth, max_depth, environment, exceptions: float(data1 == data2)
        distances = numpy.zeros((len(data2) + 1, len(data1) + 1), numpy.float32)
        # distances:list[list[float]] = [[0] * (len(data1) + 1) for y in range(len(data2) + 1)]
        for x in range(1, len(data1) + 1):
            distances[0, x] = x
        for y in range(1, len(data2) + 1):
            distances[y, 0] = y
        for y in range(len(data2)):
            for x in range(len(data1)):
                distances[y + 1, x + 1] = min(
                    distances[y + 1, x] + 1,
                    distances[y, x + 1] + 1,
                    distances[y, x] + similarity_function(data1[x], data2[y], depth + 1, max_depth, environment, exceptions),
                )
        levenshtein_distance = distances[len(data2)][len(data1)]
        max_length = len(data1) if len(data1) > len(data2) else len(data2)
        return 1 - (levenshtein_distance / max_length)

    def compare(
        self,
        data1:Sequence[d],
        data2:Sequence[d],
        environment:StructureEnvironment.ComparisonEnvironment,
    ) -> tuple[Sequence[d|D.Diff], bool, list[Trace.ErrorTrace]]:
        if data1 is data2 or data1 == data2:
            return data1, False, []
        if len(data1) * len(data2) > 10_000_000:
            raise Exceptions.SequenceTooLongError(self, len(data1), len(data2))
        exceptions:list[Trace.ErrorTrace] = []
        similarity_function = self.structure.get_similarity if self.structure is not None else lambda data1, data2, depth, max_depth, environment, exceptions: float(data1 == data2)
        compare_function:Callable[[d,d,StructureEnvironment.ComparisonEnvironment],tuple[d|D.Diff[d],bool,list[Trace.ErrorTrace]]] = \
            self.structure.compare if self.structure is not None else lambda data1, data2, environment: (data1, False, []) if data1 is data2 or data1 == data2 else (D.Diff(old=data1, new=data2), True, [])

        data1_hashes:list[int] = [Hashing.hash_data(item) for item in data1]
        data2_hashes:list[int] = [Hashing.hash_data(item) for item in data2]
        
        prefix_len = sum(1 for i in takewhile(lambda a: a[0] == a[1], zip(data1_hashes, data2_hashes))) # number of items at start that are the same
        shorter_length = min(len(data1), len(data2))
        suffix_len = sum(1 for i in takewhile(lambda a: a[0] < shorter_length - prefix_len and a[1] == a[2], zip(count(), reversed(data1_hashes), reversed(data2_hashes)))) # number of items at end that are the same unless that line is included in prefix_len.
        
        distances = numpy.zeros((len(data2) + 1 - prefix_len - suffix_len, len(data1) + 1 - prefix_len - suffix_len), numpy.float32)
        # distances:list[list[float]] = [[0] * (len(data1) + 1) for y in range(len(data2) + 1)]
        path = numpy.zeros((len(data2) + 1 - prefix_len - suffix_len, len(data1) + 1 - prefix_len - suffix_len), numpy.int8)
        # path:list[list[Direction]] = [[Direction.none] * (len(data1) + 1) for y in range(len(data2) + 1)]
        for x in range(1, len(data1) + 1 - prefix_len - suffix_len):
            distances[0, x] = x
            path[0, x] = HORIZONTAL
        for y in range(1, len(data2) + 1 - prefix_len - suffix_len):
            distances[y, 0] = y
            path[y, 0] = VERTICAL
        for y in range(len(data2) - prefix_len - suffix_len):
            for x in range(len(data1) - prefix_len - suffix_len):
                deletion_cost:float = distances[y + 1, x] + self.deletion_cost
                addition_cost:float = distances[y, x + 1] + self.addition_cost
                if data1_hashes[x + prefix_len] == data2_hashes[y + prefix_len]:
                    substitution_cost = 0
                    substitution_direction = DIAGONAL_NO_CHANGE
                else:
                    substitution_cost = (1 - similarity_function(data1[x + prefix_len], data2[y + prefix_len], 1, self.max_similarity_descendent_depth, environment, exceptions)) * self.substitution_cost
                    substitution_direction = DIAGONAL_SUBSTITUTION
                if substitution_cost < addition_cost and substitution_cost < deletion_cost:
                    cost = substitution_cost
                    direction = substitution_direction
                elif addition_cost < substitution_cost and addition_cost < deletion_cost:
                    cost = addition_cost
                    direction = VERTICAL
                else:
                    cost = deletion_cost
                    direction = HORIZONTAL
                path[y + 1, x + 1] = direction
                distances[y + 1, x + 1] = cost
        # retrace steps
        has_changes = False
        output:list[d|D.Diff] = []
        x = len(data1) - prefix_len - suffix_len # x and y represent (at first) the bottom right corner of an edit distance matrix.
        y = len(data2) - prefix_len - suffix_len
        while x != 0 or y != 0:
            path_item:int = path[y, x]
            if path_item == DIAGONAL_NO_CHANGE:
                x -= 1; y -= 1
                output.append(data1[x + prefix_len]) # data1[x] and data2[y] must be equal
            elif path_item == DIAGONAL_SUBSTITUTION:
                has_changes = True
                x -= 1; y -= 1
                comparison, any_changes, new_exceptions = compare_function(data1[x + prefix_len], data2[y + prefix_len], environment)
                has_changes = has_changes or any_changes
                exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
                output.append(comparison)
            elif path_item == VERTICAL:
                has_changes = True
                y -= 1
                output.append(D.Diff(new=data2[y + prefix_len]))
            elif path_item == HORIZONTAL:
                has_changes = True
                x -= 1
                output.append(D.Diff(old=data1[x + prefix_len]))
            else:
                raise Exceptions.InvalidStateError("NONE in middle of table!")
        output.reverse() # the above process starts at the end of the sequence and goes backward

        output = data1[:prefix_len] + output + data1[len(data1)-suffix_len:] # type: ignore

        if type(data1) == list:
            actual_output:Sequence[d|D.Diff] = output
        else:
            # like, what's the point of having a MutableSequence type if it
            # just doesn't work? If I try using it in this function then it
            # will just act like a normal list without the special features
            # that Sequence has. It's really pissing me off and it's why I'm
            # doing weird stuff like this.
            actual_output = type(data1)(output) # type: ignore
        return actual_output, has_changes, exceptions
