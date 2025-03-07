from itertools import count, takewhile
from typing import Callable

import Structure.Delegate.Delegate as Delegate
import Structure.Normalizer as Normalizer
import Structure.PrimitiveStructure as PrimitiveStructure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions


class StringStructure(PrimitiveStructure.PrimitiveStructure[str]):

    __slots__ = (
        "max_similarity_ancestor_depth",
        "similarity_function",
    )

    def __init__(
        self,
        name: str,
        max_similarity_ancestor_depth:int|None,
        children_has_normalizer: bool,
    ) -> None:
        super().__init__(name, children_has_normalizer)

        self.max_similarity_ancestor_depth = max_similarity_ancestor_depth
        self.similarity_function:Callable[[str],str]|None = None

    def link_substructures(
        self,
        delegate:Delegate.Delegate|None,
        types:tuple[type,...],
        normalizer:list[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
        tags:set[StructureTag.StructureTag],
        similarity_function:Callable[[str],str]|None,
        children_tags:set[StructureTag.StructureTag],
    ) -> None:
        super().link_substructures(delegate, types, normalizer, pre_normalized_types, tags, children_tags)

        self.similarity_function = similarity_function

    def get_levenshtein_distance(self, data1:str, data2:str) -> int:
        distances:list[list[int]] = [[0] * (len(data1) + 1) for y in range(len(data2) + 1)]

        prefix_len = sum(1 for i in takewhile(lambda a: a[0] == a[1], zip(data1, data2))) # number of items at start that are the same
        shorter_length = min(len(data1), len(data2))
        suffix_len = sum(1 for i in takewhile(lambda a: a[0] < shorter_length - prefix_len and a[1] == a[2], zip(count(), reversed(data1), reversed(data2)))) # number of items at end that are the same unless that line is included in prefix_len.
        if (len(data1) - prefix_len - suffix_len) * (len(data2) - prefix_len - suffix_len) > 1_000_000:
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

    def get_similarity(self, data1: str, data2: str, depth:int, max_depth:int|None, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace], branch:int) -> float:
        if (max_depth is not None and depth > max_depth) or (self.max_similarity_ancestor_depth is not None and depth > self.max_similarity_ancestor_depth):
            return float(data1 == data2)
        if self.similarity_function is not None:
            data1 = self.similarity_function(data1)
            data2 = self.similarity_function(data2)
        if len(data1) == 0 and len(data2) == 0:
            return 1.0
        elif data1 == data2:
            return 1.0
        max_length = len(data1) if len(data1) > len(data2) else len(data2)
        levenshtein_distance = self.get_levenshtein_distance(data1, data2)
        return 1 - (levenshtein_distance / max_length)
