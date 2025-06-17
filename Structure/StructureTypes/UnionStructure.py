from typing import Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.PassthroughStructure import PassthroughStructure
from Structure.Structure import Structure
from Structure.StructureEnvironment import PrinterEnvironment
from Structure.Uses import StructureUse, UnionStructureUse, UsageTracker, Use
from Utilities.Exceptions import StructureTypeError
from Utilities.Trace import Trace
from Utilities.TypeUtilities import TypeDict


class UnionStructure[D, BO, CO](PassthroughStructure[D, BO, CO]):

    __slots__ = (
        "substructures",
    )

    def link_union_structure(
        self,
        substructures:TypeDict[D,Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None],
    ) -> None:
        self.substructures = substructures

    def get_structure(self, data: D, trace: Trace, environment: PrinterEnvironment) -> Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None:
        if (output := self.substructures.get(type(data), ...)) is ...:
            trace.exception(StructureTypeError(tuple(self.substructures.keys()), type(data), "Data"))
            return None
        return output

    def iter_structures(self) -> Sequence[Structure]:
        return [structure for structure in self.substructures.values() if structure is not None]

    def get_uses(self, data: Con[D], usage_tracker:UsageTracker, trace: Trace, environment: PrinterEnvironment) -> OrderedSet[Use]:
        if not usage_tracker.still_used(self): return OrderedSet(())
        with trace.enter(self, self.name, data):
            output:OrderedSet[Use] = OrderedSet(())
            output.update(super().get_uses(data, usage_tracker, trace, environment))
            for this_type in self.substructures.keys():
                if isinstance(data.data, this_type):
                    output.add(UnionStructureUse(this_type, self, usage_tracker, StructureUse(self, None)))
                    break
            else: StructureTypeError(tuple(self.substructures.keys()), type(data.data), "Data")
            return output
        return OrderedSet(())

    def get_all_uses(self, memo:set[Structure]) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        output:OrderedSet[Use] = OrderedSet(())
        output.update(super().get_all_uses(memo))
        self_use = StructureUse(self, None)
        for type, substructure in self.substructures.items():
            output.add(UnionStructureUse(type, self, None, self_use))
            if substructure is not None:
                output.update(substructure.get_all_uses(memo))
        return output
