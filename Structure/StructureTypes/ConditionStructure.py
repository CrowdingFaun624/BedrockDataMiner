from typing import Sequence

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.Filter import Filter
from Structure.PassthroughStructure import PassthroughStructure
from Structure.Structure import Structure
from Structure.StructureEnvironment import PrinterEnvironment
from Utilities.Exceptions import ConditionStructureFilterError, StructureTypeError
from Utilities.Trace import Trace


class ConditionStructure[D, BO, CO](PassthroughStructure[D, BO, CO]):

    __slots__ = (
        "branch_types",
        "filters",
        "structures",
    )

    def link_condition_structure(
        self,
        substructures:Sequence[tuple[tuple[type,...], Filter|None, Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None]],
    ) -> None:
        self.branch_types:list[tuple[type,...]] = [substructure[0] for substructure in substructures]
        self.filters:list[Filter|None] = [substructure[1] for substructure in substructures]
        self.structures:list[Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None] = [substructure[2] for substructure in substructures]

    def type_check_extra(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> None:
        branch = environment.structure_info.evaluate(self, self.filters)
        if branch is None:
            trace.exception(ConditionStructureFilterError(self, environment.structure_info))
            return
        if not isinstance(data.data, self.branch_types[branch]):
            trace.exception(StructureTypeError(self.branch_types[branch], type(data.data), "Data"))

    def get_structure(self, data: D, trace: Trace, environment: PrinterEnvironment) -> Structure[D, Con[D], Don[D], Don[D] | Diff[Don[D]], BO, CO] | None:
        branch = environment.structure_info.evaluate(self, self.filters)
        if branch is None:
            trace.exception(ConditionStructureFilterError(self, environment.structure_info))
            return None
        return self.structures[branch]

    def iter_structures(self) -> Sequence[Structure]:
        return [structure for structure in self.structures if structure is not None]
