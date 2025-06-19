from types import EllipsisType
from typing import Mapping, Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.PassthroughStructure import PassthroughStructure
from Structure.Structure import Structure
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Structure.Uses import Region, StructureUse, TypeUse, UsageTracker, Use
from Utilities.Exceptions import StructureTypeError
from Utilities.Trace import Trace

foo = False

class BranchlessStructure[D, BO, CO](PassthroughStructure[D, BO, CO]):

    __slots__ = (
        "structure",
        "this_types",
    )

    def link_branchless_structure(
        self,
        structure:Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None,
        this_types:tuple[type,...],
    ) -> None:
        self.structure = structure
        self.this_types = this_types

    def iter_structures(self) -> Sequence[Structure]:
        return (self.structure,) if self.structure is not None else ()

    def type_check_extra(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> None:
        if not isinstance(data.data, self.this_types):
            trace.exception(StructureTypeError(self.this_types, type(data.data), "Data"))

    def get_structure(self, data: D, trace: Trace, environment: PrinterEnvironment) -> Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None:
        return self.structure

    def diffize(self, data: Con[D], bundle: tuple[int, ...], trace: Trace, environment: ComparisonEnvironment) -> Mapping[tuple[int,...],Don[D]]|EllipsisType:
        with trace.enter(self, self.name, data):
            if self.structure is None:
                return {bundle: data.as_don(bundle)}
            else:
                return self.structure.diffize(data, bundle, trace, environment)
        return ...

    def get_uses(self, data: Con[D], usage_tracker: UsageTracker, parent_use:Use|None, trace: Trace, environment: PrinterEnvironment) -> OrderedSet[Use]:
        if not usage_tracker.still_used(self): return OrderedSet(())
        with trace.enter(self, self.name, data):
            output:OrderedSet[Use] = OrderedSet(())
            output.update(super().get_uses(data, usage_tracker, parent_use, trace, environment))
            for this_type in self.this_types:
                if isinstance(data.data, this_type):
                    output.add(TypeUse(this_type, Region.this_types, StructureUse(self, None, parent_use), usage_tracker))
                    break
            else: raise StructureTypeError(self.this_types, type(data.data), "Data")
            return output
        return OrderedSet(())

    def get_all_uses(self, memo:set[Structure], parent_use:Use|None) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        output:OrderedSet[Use] = OrderedSet(())
        output.update(super().get_all_uses(memo, parent_use))
        self_use = StructureUse(self, None, parent_use)
        for this_type in self.this_types:
            output.add(TypeUse(this_type, Region.this_types, self_use, None))
        if self.structure is not None:
            output.update(self.structure.get_all_uses(memo, self_use if self.structure.is_inline else None))
        return output

    def compare(self, datas: tuple[tuple[int, Con[D]], ...], trace: Trace, environment: ComparisonEnvironment) -> tuple[Don[D]|Diff[Don[D]]|EllipsisType, bool, bool]:
        with trace.enter(self, self.name, datas):

            if self.structure is None:
                consecutive_similarities = self.get_consecutive_similarities(datas, trace, environment)
                return Diff(self.get_without_structure_comparison(consecutive_similarities), False), True, False

            else:
                comparison, any_changes, internal_changes = self.structure.compare(datas, trace, environment)

            if comparison is ...:
                # error has occurred in `structure.compare`
                return ..., False, False
            elif isinstance(comparison, Diff):
                return comparison, any_changes, internal_changes
            else:
                return Diff({tuple(branch for branch, _ in datas): comparison}, internal_changes), any_changes, internal_changes

        return ..., False, False
