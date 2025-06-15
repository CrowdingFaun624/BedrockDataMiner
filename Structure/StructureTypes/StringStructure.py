from itertools import count, takewhile
from typing import Callable, Sequence

from Structure.PrimitiveStructure import PrimitiveStructure
from Structure.SimilarityCache import SimilarityCache
from Structure.SimpleContainer import SCon
from Structure.StructureEnvironment import ComparisonEnvironment
from Utilities.Exceptions import SequenceTooLongError
from Utilities.Trace import Trace


class StringStructure[D, BO, CO](PrimitiveStructure[D, BO, CO]):

    __slots__ = (
        "max_square_length",
        "similarity_cache",
        "similarity_function",
        "similarity_weight_function",
    )

    def link_string_structure(
        self,
        max_square_length:int,
        similarity_function:Callable[[SCon[D]], str],
        similarity_weight_function:Callable[[str],Sequence[int]],
    ) -> None:
        self.max_square_length = max_square_length
        self.similarity_function = similarity_function
        self.similarity_weight_function = similarity_weight_function

        self.similarity_cache:SimilarityCache[SCon[D]] = SimilarityCache()

    def get_similarity_caches(self) -> Sequence[SimilarityCache]:
        return (self.similarity_cache,)

    def get_levenshtein_distance(self, data1:str, data2:str, similarity_weight1:Sequence[int], similarity_weight2:Sequence[int]) -> int:
        prefix_len = sum(1 for i in takewhile(lambda a: a[0] == a[1], zip(data1, data2))) # number of items at start that are the same
        shorter_length = min(len(data1), len(data2))
        suffix_len = sum(1 for i in takewhile(lambda a: a[0] < shorter_length - prefix_len and a[1] == a[2], zip(count(), reversed(data1), reversed(data2)))) # number of items at end that are the same unless that line is included in prefix_len.
        distances:list[list[int]] = [[0] * (len(data1) + 1 - prefix_len - suffix_len) for y in range(len(data2) + 1 - prefix_len - suffix_len)]
        if (len(data1) - prefix_len - suffix_len) * (len(data2) - prefix_len - suffix_len) > self.max_square_length:
            raise SequenceTooLongError(self, len(data1), len(data2))

        for x in range(1, len(data1) + 1 - prefix_len - suffix_len):
            distances[0][x] = distances[0][x - 1] + similarity_weight1[x + prefix_len - 1]
        for y in range(1, len(data2) + 1 - prefix_len - suffix_len):
            distances[y][0] = distances[y - 1][0] + similarity_weight2[y + prefix_len - 1]
        for y in range(len(data2) - prefix_len - suffix_len):
            for x in range(len(data1) - prefix_len - suffix_len):
                distances[y + 1][x + 1] = min(
                    distances[y+1][x] + similarity_weight1[x + prefix_len],
                    distances[y][x+1] + similarity_weight2[y + prefix_len],
                    distances[y][x] + int(data1[x + prefix_len] != data2[y + prefix_len]) * (similarity_weight1[x + prefix_len] + similarity_weight2[y + prefix_len]),
                )
        return distances[len(data2) - prefix_len - suffix_len][len(data1) - prefix_len - suffix_len]

    def get_similarity(self, data1: SCon[D], data2: SCon[D], branch1: int, branch2: int, trace: Trace, environment: ComparisonEnvironment) -> tuple[float, bool]:
        with trace.enter(self, self.name, (data1, data2)):
            if (output := self.similarity_cache.get(data1, data2, structure_info1 := environment[branch1].structure_info, structure_info2 := environment[branch2].structure_info)) is not None:
                return output
            data1_str = self.similarity_function(data1)
            data2_str = self.similarity_function(data2)
            similarity_weight1 = self.similarity_weight_function(data1_str)
            similarity_weight2 = self.similarity_weight_function(data2_str)
            if len(data1_str) == 0 and len(data2_str) == 0:
                return self.similarity_cache.set((1.0, True), data1, data2, structure_info1, structure_info2)
            elif data1_str == data2_str:
                # the one situation where the boolean may not necessarily equal the float.
                return self.similarity_cache.set((1.0, data1 == data2), data1, data2, structure_info1, structure_info2)
            max_weight = sum(similarity_weight1) + sum(similarity_weight2)
            levenshtein_distance = self.get_levenshtein_distance(data1_str, data2_str, similarity_weight1, similarity_weight2)
            return self.similarity_cache.set((1 - (levenshtein_distance / max_weight), levenshtein_distance == 0), data1, data2, structure_info1, structure_info2)
        return 0.0, False
