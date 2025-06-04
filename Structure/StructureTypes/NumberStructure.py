from math import exp
from typing import Callable, Container

from Structure.PrimitiveStructure import PrimitiveStructure
from Structure.SimilarityCache import SimilarityCache
from Structure.SimpleContainer import SCon
from Structure.StructureEnvironment import ComparisonEnvironment
from Structure.StructureInfo import StructureInfo
from Utilities.Trace import Trace


class NumberStructure[D, BO, CO](PrimitiveStructure[D, BO, CO]):

    __slots__ = (
        "normal_value",
        "similarity_cache",
        "similarity_function",
    )

    def link_number_structure(
        self,
        normal_value:float, # normal_value > 0
        similarity_function:Callable[[SCon[D]], float],
    ) -> None:
        self.normal_value = normal_value
        self.similarity_function = similarity_function

        self.similarity_cache:SimilarityCache[SCon[D]] = SimilarityCache()

    def clear_similarity_cache(self, keep: Container[StructureInfo]) -> None:
        self.similarity_cache.clear(keep)

    def get_similarity(self, data1: SCon[D], data2: SCon[D], branch1: int, branch2: int, trace: Trace, environment: ComparisonEnvironment) -> tuple[float, bool]:
        with trace.enter(self, self.name, (data1, data2)):
            if (output := self.similarity_cache.get(data1, data2, structure_info1 := environment[branch1].structure_info, structure_info2 := environment[branch2].structure_info)) is not None:
                return output
            data1_num = self.similarity_function(data1)
            data2_num = self.similarity_function(data2)
            if data1_num == data2_num:
                return self.similarity_cache.set((1.0, True), data1, data2, structure_info1, structure_info2)
            # normal curve
            return self.similarity_cache.set((exp(-0.5 * ((data1_num - data2_num) / self.normal_value) ** 2), False), data1, data2, structure_info1, structure_info2)
        return 0.0, False
