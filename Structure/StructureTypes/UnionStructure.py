from typing import Sequence

import Structure.Container as Con
import Structure.Difference as Diff
import Structure.PassthroughStructure as PassthroughStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace


class UnionStructure[D, BO, CO](PassthroughStructure.PassthroughStructure[D, BO, CO]):

    __slots__ = (
        "substructures",
    )

    def link_union_structure(
        self,
        substructures:dict[type,Structure.Structure[D, Con.Con[D], Con.Don[D], Con.Don[D]|Diff.Diff[Con.Don[D]], BO, CO]|None],
    ) -> None:
        self.substructures = substructures

    def get_structure(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Structure.Structure[D, Con.Con[D], Con.Don[D], Con.Don[D]|Diff.Diff[Con.Don[D]], BO, CO]|None:
        if (output := self.substructures.get(type(data), ...)) is ...:
            this_types:set[type] = set(self.substructures.keys())
            trace.exception(Exceptions.StructureTypeError(tuple(this_types), type(data), "Data"))
            return None
        return output

    def iter_structures(self) -> Sequence[Structure.Structure]:
        return [structure for structure in self.substructures.values() if structure is not None]
