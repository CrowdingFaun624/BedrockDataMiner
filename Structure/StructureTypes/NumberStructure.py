from math import exp
from typing import Callable

import Structure.PrimitiveStructure as PrimitiveStructure
import Structure.SimpleContainer as SCon
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Trace as Trace


class NumberStructure[D, BO, CO](PrimitiveStructure.PrimitiveStructure[D, BO, CO]):

    __slots__ = (
        "normal_value",
        "similarity_function",
    )

    def link_number_structure(
        self,
        normal_value:float, # normal_value > 0
        similarity_function:Callable[[SCon.SCon[D]], float],
    ) -> None:
        self.normal_value = normal_value
        self.similarity_function = similarity_function

    def get_similarity(self, data1: SCon.SCon[D], data2: SCon.SCon[D], branch1: int, branch2: int, trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[float, bool]:
        with trace.enter(self, self.name, (data1, data2)):
            data1_num = self.similarity_function(data1)
            data2_num = self.similarity_function(data2)
            if data1_num == data2_num:
                return 1.0, True
            # normal curve
            return exp(-0.5 * ((data1_num - data2_num) / self.normal_value) ** 2), False
        return 0.0, False
