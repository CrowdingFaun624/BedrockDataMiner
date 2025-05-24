from itertools import count, takewhile
from typing import Callable

import Structure.PrimitiveStructure as PrimitiveStructure
import Structure.SimpleContainer as SCon
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace


class StringStructure[D, BO, CO](PrimitiveStructure.PrimitiveStructure[D, BO, CO]):

    __slots__ = (
        "max_square_length",
        "similarity_function",
    )

    def link_string_structure(
        self,
        max_square_length:int,
        similarity_function:Callable[[SCon.SCon[D]], str],
    ) -> None:
        self.max_square_length = max_square_length
        self.similarity_function = similarity_function

    def get_levenshtein_distance(self, data1:str, data2:str) -> int:
        distances:list[list[int]] = [[0] * (len(data1) + 1) for y in range(len(data2) + 1)]

        prefix_len = sum(1 for i in takewhile(lambda a: a[0] == a[1], zip(data1, data2))) # number of items at start that are the same
        shorter_length = min(len(data1), len(data2))
        suffix_len = sum(1 for i in takewhile(lambda a: a[0] < shorter_length - prefix_len and a[1] == a[2], zip(count(), reversed(data1), reversed(data2)))) # number of items at end that are the same unless that line is included in prefix_len.
        if (len(data1) - prefix_len - suffix_len) * (len(data2) - prefix_len - suffix_len) > self.max_square_length:
            raise Exceptions.SequenceTooLongError(self, len(data1), len(data2))

        for x in range(1, len(data1) + 1 - prefix_len - suffix_len):
            distances[0][x] = x
        for y in range(1, len(data2) + 1 - prefix_len - suffix_len):
            distances[y][0] = y
        for y in range(len(data2) - prefix_len - suffix_len):
            for x in range(len(data1) - prefix_len - suffix_len):
                distances[y + 1][x + 1] = min(
                    distances[y+1][x] + 1,
                    distances[y][x+1] + 1,
                    distances[y][x] + int(data1[x + prefix_len] != data2[y + prefix_len]),
                )
        return distances[len(data2) - prefix_len - suffix_len][len(data1) - prefix_len - suffix_len]

    def get_similarity(self, data1: SCon.SCon[D], data2: SCon.SCon[D], branch1: int, branch2: int, trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[float, bool]:
        with trace.enter(self, self.name, (data1, data2)):
            data1_str = self.similarity_function(data1)
            data2_str = self.similarity_function(data2)
            if len(data1_str) == 0 and len(data2_str) == 0:
                return 1.0, True
            elif data1_str == data2_str:
                return 1.0, data1 == data2 # the one situation where the boolean may not necessarily equal the float.
            max_length = max(len(data1_str), len(data2_str))
            levenshtein_distance = self.get_levenshtein_distance(data1_str, data2_str)
            return 1 - (levenshtein_distance / max_length), levenshtein_distance == 0
        return 0.0, False
