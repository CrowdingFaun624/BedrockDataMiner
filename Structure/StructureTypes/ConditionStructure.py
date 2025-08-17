from typing import AbstractSet, Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.DataPath import DataPath
from Structure.Difference import Diff
from Structure.Filter import Filter
from Structure.Key import Key
from Structure.PassthroughStructure import PassthroughStructure
from Structure.Structure import Structure
from Structure.StructureEnvironment import PrinterEnvironment
from Structure.StructureTag import StructureTag
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
        "branch_tags",
        "branch_types",
        "keys",
        "filters",
        "structures",
    )

    def link_condition_structure(
        self,
        keys:Sequence[Key],
    ) -> None:
        self.keys = keys

    def finalize_condition_structure(self) -> None:
        self.branch_tags:Sequence[AbstractSet[StructureTag]] = [key.tags for key in self.keys]
        self.branch_types:Sequence[tuple[type,...]] = [key.types for key in self.keys]
        self.filters:Sequence[Filter|None] = [key.filter for key in self.keys]
        self.structures:Sequence[Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None] = [key.structure for key in self.keys]
        del self.keys

    def type_check_extra(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> None:
        branch = environment.structure_info.evaluate(self, self.filters)
        if branch is None:
            trace.exception(ConditionStructureFilterError(self, environment.structure_info))
            return
        if not isinstance(data.data, self.branch_types[branch]):
            trace.exception(StructureTypeError(self.branch_types[branch], type(data.data), "Data"))

    def get_tag_paths_extra(self, data: Con[D], tag: StructureTag, data_path: DataPath, trace: Trace, environment: PrinterEnvironment) -> Sequence[DataPath]:
        branch = environment.structure_info.evaluate(self, self.filters)
        if branch is None:
            trace.exception(ConditionStructureFilterError(self, environment.structure_info))
            return ()
        tags = self.branch_tags[branch]
        if tag in tags:
            return (data_path.copy(...).embed(data.data),)
        return ()

    def get_structure(self, data: D, trace: Trace, environment: PrinterEnvironment) -> Structure[D, Con[D], Don[D], Don[D] | Diff[Don[D]], BO, CO] | None:
        branch = environment.structure_info.evaluate(self, self.filters)
        if branch is None:
            trace.exception(ConditionStructureFilterError(self, environment.structure_info))
            return None
        return self.structures[branch]

    def iter_structures(self) -> Sequence[Structure]:
        return [structure for structure in self.structures if structure is not None]

    def get_uses(self, data: Con[D], usage_tracker:UsageTracker, parent_use:Use|None, trace: Trace, environment: PrinterEnvironment) -> OrderedSet[Use]:
        if not usage_tracker.still_used(self): return OrderedSet(())
        with trace.enter(self, self.trace_name, data):
            output:OrderedSet[Use] = OrderedSet(())
            output.update(super().get_uses(data, usage_tracker, parent_use, trace, environment))
            branch = environment.structure_info.evaluate(self, self.filters)
            if branch is None:
                trace.exception(ConditionStructureFilterError(self, environment.structure_info))
                return output
            condition_structure_use = ConditionStructureUse(branch, self, usage_tracker, StructureUse(self, None, parent_use))
            output.add(condition_structure_use)
            for this_type in self.branch_types[branch]:
                if isinstance(data.data, this_type):
                    output.add(TypeUse(this_type, Region.this_types, condition_structure_use, usage_tracker))
                    break
            else: raise StructureTypeError(self.branch_types[branch], type(data.data), "Data")
            return output
        return OrderedSet(())

    def get_all_uses(self, memo: set[Structure], parent_use:Use|None) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        output:OrderedSet[Use] = OrderedSet(())
        output.update(super().get_all_uses(memo, parent_use))
        self_use = StructureUse(self, None, parent_use)
        for branch, (types, structure) in enumerate(zip(self.branch_types, self.structures, strict=True)):
            if structure is not None:
                output.update(structure.get_all_uses(memo, self_use if structure.is_inline else None))
            condition_structure_use = ConditionStructureUse(branch, self, None, self_use)
            output.add(condition_structure_use)
            for type in types:
                output.add(TypeUse(type, Region.this_types, condition_structure_use, None))
        return output
