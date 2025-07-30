from types import EllipsisType
from typing import Any, Sequence

from Structure.Function import Function
from Structure.StructureEnvironment import PrinterEnvironment
from Structure.WithinStructure import WithinStructure
from Utilities.Exceptions import NormalizerEllipsisError
from Utilities.Trace import Trace


class NormalizerStructure[A, B, BO, CO](WithinStructure[A, B, BO, CO]):

    __slots__ = (
        "functions",
    )

    def link_normalizer_structure(
        self,
        functions:Sequence[Function],
    ) -> None:
        self.functions = functions

    def get_insides(self, data: A, trace: Trace, environment: PrinterEnvironment) -> B|EllipsisType:
        intermediate_data:Any = data
        for function in self.functions:
            with trace.enter(function, function.trace_name, intermediate_data):
                try:
                    intermediate_data = function(intermediate_data)
                except Exception as e:
                    trace.exception(e)
                    return ...
        if intermediate_data is ...:
            trace.exception(NormalizerEllipsisError(self))
            return ...
        return intermediate_data
