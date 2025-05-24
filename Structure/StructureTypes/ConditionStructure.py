from typing import Sequence

import Structure.Container as Con
import Structure.Difference as Diff
import Structure.Filter as Filter
import Structure.PassthroughStructure as PassthroughStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace


class ConditionStructure[D, BO, CO](PassthroughStructure.PassthroughStructure[D, BO, CO]):

    __slots__ = (
        "branch_types",
        "filters",
        "structures",
    )

    def link_condition_structure(
        self,
        substructures:Sequence[tuple[tuple[type,...], Filter.Filter|None, Structure.Structure[D, Con.Con[D], Con.Don[D], Con.Don[D]|Diff.Diff[Con.Don[D]], BO, CO]|None]],
    ) -> None:
        self.branch_types:list[tuple[type,...]] = [substructure[0] for substructure in substructures]
        self.filters:list[Filter.Filter|None] = [substructure[1] for substructure in substructures]
        self.structures:list[Structure.Structure[D, Con.Con[D], Con.Don[D], Con.Don[D]|Diff.Diff[Con.Don[D]], BO, CO]|None] = [substructure[2] for substructure in substructures]

    def type_check_extra(self, data: Con.Con[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> None:
        branch = environment.structure_info.evaluate(self, self.filters)
        if branch is None:
            trace.exception(Exceptions.ConditionStructureFilterError(self, environment.structure_info))
            return
        if not isinstance(data.data, self.branch_types[branch]):
            trace.exception(Exceptions.StructureTypeError(self.branch_types[branch], type(data.data), "Data"))

    def get_structure(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Structure.Structure[D, Con.Con[D], Con.Don[D], Con.Don[D] | Diff.Diff[Con.Don[D]], BO, CO] | None:
        branch = environment.structure_info.evaluate(self, self.filters)
        if branch is None:
            trace.exception(Exceptions.ConditionStructureFilterError(self, environment.structure_info))
            return None
        return self.structures[branch]

    def iter_structures(self) -> Sequence[Structure.Structure]:
        return [structure for structure in self.structures if structure is not None]
