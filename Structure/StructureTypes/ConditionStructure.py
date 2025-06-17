from typing import Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.Filter import Filter
from Structure.PassthroughStructure import PassthroughStructure
from Structure.Structure import Structure
from Structure.StructureEnvironment import PrinterEnvironment
from Structure.Uses import (
    ConditionStructureUse,
    Region,
    StructureUse,
    TypeUse,
    UsageTracker,
    Use,
)
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

    def get_uses(self, data: Con[D], usage_tracker:UsageTracker, trace: Trace, environment: PrinterEnvironment) -> OrderedSet[Use]:
        if not usage_tracker.still_used(self): return OrderedSet(())
        with trace.enter(self, self.name, data):
            output:OrderedSet[Use] = OrderedSet(())
            output.update(super().get_uses(data, usage_tracker, trace, environment))
            branch = environment.structure_info.evaluate(self, self.filters)
            if branch is None:
                trace.exception(ConditionStructureFilterError(self, environment.structure_info))
                return output
            condition_structure_use = ConditionStructureUse(branch, self, usage_tracker, StructureUse(self, None))
            output.add(condition_structure_use)
            for this_type in self.branch_types[branch]:
                if isinstance(data.data, this_type):
                    output.add(TypeUse(this_type, Region.this_types, condition_structure_use, usage_tracker))
                    break
            else: raise StructureTypeError(self.branch_types[branch], type(data.data), "Data")
            return output
        return OrderedSet(())

    def get_all_uses(self, memo: set[Structure]) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        output:OrderedSet[Use] = OrderedSet(())
        output.update(super().get_all_uses(memo))
        self_use = StructureUse(self, None)
        for branch, (types, structure) in enumerate(zip(self.branch_types, self.structures, strict=True)):
            if structure is not None:
                output.update(structure.get_all_uses(memo))
            condition_structure_use = ConditionStructureUse(branch, self, None, self_use)
            output.add(condition_structure_use)
            for type in types:
                output.add(TypeUse(type, Region.this_types, condition_structure_use, None))
        return output
