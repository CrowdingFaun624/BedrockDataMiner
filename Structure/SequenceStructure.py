from itertools import count, takewhile
from typing import TYPE_CHECKING, Callable, Sequence, cast

import numpy

import Component.Types as Types
import Structure.AbstractIterableStructure as AbstractIterableStructure
import Structure.Difference as D
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

NONE = 0
HORIZONTAL = 1
VERTICAL = 2
DIAGONAL_SUBSTITUTION = 3
DIAGONAL_NO_CHANGE = 4

class SequenceStructure[d](AbstractIterableStructure.AbstractIterableStructure[d]):
    '''
    Sequential data structure. Uses levenshtein distance for comparing.
    '''

    __slots__ = (
        "addition_cost",
        "deletion_cost",
        "substitution_cost",
    )

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

    def get_similarity(self, data1: Sequence[d|D.Diff[d]], data2: Sequence[d], depth:int, max_depth:int|None, environment: StructureEnvironment.ComparisonEnvironment, exceptions: list[Trace.ErrorTrace], branch:int) -> float:
        if (max_depth is not None and depth > max_depth) or (self.max_similarity_ancestor_depth is not None and depth > self.max_similarity_ancestor_depth):
            if branch == 0:
                return float(data1 == data2)
            else:
                return float(Structure.get_data_at_branch(data1, branch) == data2)

        data1_hashes:list[int] = [Types.hash_data(D.last_value(item)) for item in data1]
        data2_hashes:list[int] = [Types.hash_data(item) for item in data2]
        prefix_len = sum(1 for i in takewhile(lambda a: a[0] == a[1], zip(data1_hashes, data2_hashes))) # number of items at start that are the same
        shorter_length = min(len(data1), len(data2))
        suffix_len = sum(1 for i in takewhile(lambda a: a[0] < shorter_length - prefix_len and a[1] == a[2], zip(count(), reversed(data1_hashes), reversed(data2_hashes)))) # number of items at end that are the same unless that line is included in prefix_len.
        if (len(data1) - prefix_len - suffix_len) * (len(data2) - prefix_len - suffix_len) > 10_000_000:
            raise Exceptions.SequenceTooLongError(self, len(data1), len(data2))

        similarity_function:Callable[[d,d,int,int|None,StructureEnvironment.ComparisonEnvironment,list[Trace.ErrorTrace],int],float] =\
            self.structure.get_similarity if self.structure is not None else lambda data1, data2, depth, max_depth, environment, exceptions, branch: float(data1 == data2)
        distances = numpy.zeros((len(data2) + 1 - prefix_len - suffix_len, len(data1) + 1 - prefix_len - suffix_len), numpy.float32)
        # distances:list[list[float]] = [[0] * (len(data1) + 1 - prefix_len - suffix_len) for y in range(len(data2) + 1 - prefix_len - suffix_len)]
        for x in range(1, len(data1) + 1 - prefix_len - suffix_len):
            distances[0, x] = x
        for y in range(1, len(data2) + 1 - prefix_len - suffix_len):
            distances[y, 0] = y
        for y in range(len(data2)):
            for x in range(len(data1)):
                distances[y + 1 + prefix_len, x + 1 + prefix_len] = min(
                    distances[y + 1 + prefix_len, x + prefix_len] + 1,
                    distances[y + prefix_len, x + 1 + prefix_len] + 1,
                    distances[y + prefix_len, x + prefix_len] + \
                        (1 if (data1_hashes[x + prefix_len] == data2_hashes[y + prefix_len])
                         else similarity_function(D.last_value(data1[x + prefix_len]), data2[y + prefix_len], depth + 1, max_depth, environment, exceptions, branch)
                        ),
                )
        levenshtein_distance = distances[len(data2) - prefix_len - suffix_len][len(data1) - prefix_len - suffix_len]
        max_length = len(data1) if len(data1) > len(data2) else len(data2) # DO NOT subtract prefix_len or suffix_len
        return 1 - (levenshtein_distance / max_length)

    def compare_sub(self, data1:d|D.Diff[d], data2:d, environment:StructureEnvironment.ComparisonEnvironment, branch:int, branches:int) -> tuple[d|D.Diff[d],bool,list[Trace.ErrorTrace]]:
        if data1 is data2 or data1 == data2:
            return data1, False, []
        elif self.structure is None:
            if isinstance(data1, D.Diff):
                data1_diff = cast("D.Diff[d]", data1)
                if data1_diff.last_value == data2:
                    return data1_diff.extend(branch+1), True, []
                else:
                    return data1_diff.append(branch+1, data2), True, []
            else:
                data1_object = cast(d, data1)
                return D.Diff(branches, {tuple(range(0,branch+1)): data1_object, (branch+1,): data2}), True, []
        elif isinstance(data1, D.Diff):
            data1_diff = cast("D.Diff[d]", data1)
            comparison, _, exceptions = self.structure.compare(data1_diff.last_value, data2, environment, branch, branches)
            return data1_diff.with_last_as(branch+1, comparison), True, exceptions
        else:
            data1_object = cast(d, data1)
            return self.structure.compare(data1_object, data2, environment, branch, branches)

    def compare(
        self,
        data1:Sequence[d|D.Diff[d]],
        data2:Sequence[d],
        environment:StructureEnvironment.ComparisonEnvironment,
        branch:int,
        branches:int,
    ) -> tuple[Sequence[d|D.Diff], bool, list[Trace.ErrorTrace]]:
        if not environment.is_multi_diff and (data1 is data2 or data1 == data2):
            return data1, False, []
        exceptions:list[Trace.ErrorTrace] = []
        similarity_function:Callable[[d,d,int,int|None,StructureEnvironment.ComparisonEnvironment,list[Trace.ErrorTrace],int],float] =\
            self.structure.get_similarity if self.structure is not None else lambda data1, data2, depth, max_depth, environment, exceptions, branch: float(data1 == data2)

        data1_hashes:list[int] = [Types.hash_data(D.last_value(item)) for item in data1]
        data2_hashes:list[int] = [Types.hash_data(item) for item in data2]

        prefix_len = sum(1 for i in takewhile(lambda a: a[0] == a[1], zip(data1_hashes, data2_hashes))) # number of items at start that are the same
        shorter_length = min(len(data1), len(data2))
        suffix_len = sum(1 for i in takewhile(lambda a: a[0] < shorter_length - prefix_len and a[1] == a[2], zip(count(), reversed(data1_hashes), reversed(data2_hashes)))) # number of items at end that are the same unless that line is included in prefix_len.

        if (len(data1) - prefix_len - suffix_len) * (len(data2) - prefix_len - suffix_len) > 10_000_000:
            raise Exceptions.SequenceTooLongError(self, len(data1), len(data2))

        distances = numpy.zeros((len(data2) + 1 - prefix_len - suffix_len, len(data1) + 1 - prefix_len - suffix_len), numpy.float32)
        path = numpy.zeros((len(data2) + 1 - prefix_len - suffix_len, len(data1) + 1 - prefix_len - suffix_len), numpy.int8)
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
                    substitution_cost = (1 - similarity_function(D.last_value(data1[x + prefix_len]), data2[y + prefix_len], 1, self.max_similarity_descendent_depth, environment, exceptions, branch)) * self.substitution_cost
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
        output:list[d|D.Diff[d]] = []
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
                comparison, any_changes, new_exceptions = self.compare_sub(data1[x + prefix_len], data2[y + prefix_len], environment, branch, branches)
                has_changes = has_changes or any_changes
                exceptions.extend(exception.add(self.name, None) for exception in new_exceptions)
                output.append(comparison)
            elif path_item == VERTICAL:
                has_changes = True
                y -= 1
                output.append(D.Diff(branches, {(branch+1,): data2[y + prefix_len]}))
            elif path_item == HORIZONTAL:
                has_changes = True
                x -= 1
                item = data1[x + prefix_len]
                output.append(item if isinstance(item, D.Diff) else D.Diff(branches, {tuple(range(0,branch+1)): item}))
            else:
                raise Exceptions.InvalidStateError("NONE in middle of table!")
        output.reverse() # the above process starts at the end of the sequence and goes backward

        # unchanged items
        actual_output1:list[d|D.Diff[d]] = []
        for item in data1[:prefix_len]:
            if isinstance(item, D.Diff):
                item = cast("D.Diff[d]", item).extend(branch+1)
            elif TYPE_CHECKING:
                item = cast(d, item)
            actual_output1.append(item)
        actual_output1.extend(output)
        for item in data1[len(data1)-suffix_len:]:
            if isinstance(item, D.Diff):
                item = cast("D.Diff[d]", item).extend(branch+1)
            elif TYPE_CHECKING:
                item = cast(d, item)
            actual_output1.append(item)

        if type(data1) == list:
            actual_output2:Sequence[d|D.Diff] = actual_output1
        else:
            # like, what's the point of having a MutableSequence type if it
            # just doesn't work? If I try using it in this function then it
            # will just act like a normal list without the special features
            # that Sequence has. It's really pissing me off and it's why I'm
            # doing weird stuff like this.
            actual_output2 = type(data1)(actual_output1) # type: ignore
        return actual_output2, has_changes, exceptions
