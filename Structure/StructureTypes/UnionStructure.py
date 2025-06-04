from typing import Sequence

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.PassthroughStructure import PassthroughStructure
from Structure.Structure import Structure
from Structure.StructureEnvironment import PrinterEnvironment
from Utilities.Exceptions import StructureTypeError
from Utilities.Trace import Trace


class UnionStructure[D, BO, CO](PassthroughStructure[D, BO, CO]):

    __slots__ = (
        "substructures",
    )

    def link_union_structure(
        self,
        substructures:dict[type,Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None],
    ) -> None:
        self.substructures = substructures

    def get_structure(self, data: D, trace: Trace, environment: PrinterEnvironment) -> Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None:
        if (output := self.substructures.get(type(data), ...)) is ...:
            this_types:set[type] = set(self.substructures.keys())
            trace.exception(StructureTypeError(tuple(this_types), type(data), "Data"))
            return None
        return output

    def iter_structures(self) -> Sequence[Structure]:
        return [structure for structure in self.substructures.values() if structure is not None]
