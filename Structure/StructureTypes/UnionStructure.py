from typing import AbstractSet, Mapping, Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.DataPath import DataPath
from Structure.Difference import Diff
from Structure.Key import Key
from Structure.PassthroughStructure import PassthroughStructure
from Structure.Structure import Structure
from Structure.StructureEnvironment import PrinterEnvironment
from Structure.StructureTag import StructureTag
from Structure.Uses import StructureUse, UnionStructureUse, UsageTracker, Use
from Utilities.Exceptions import StructureTypeError
from Utilities.Trace import Trace


class UnionStructure[D, BO, CO](PassthroughStructure[D, BO, CO]):

    __slots__ = (
        "keys",
        "substructures",
        "union_tags",
    )

    def link_union_structure(self, keys:Sequence[Key]) -> None:
        self.keys = keys

    def finalize_union_structure(self) -> None:
        for key in self.keys:
            key.finalize_key()
        self.substructures:Mapping[type[D], Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None] = {type: key.structure for key in self.keys for type in key.types}
        self.union_tags:Mapping[type[D], AbstractSet[StructureTag]] = {type: key.tags for key in self.keys for type in key.types if len(key.tags) > 0}
        del self.keys

    def get_structure(self, data: D, trace: Trace, environment: PrinterEnvironment) -> Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None:
        if (output := self.substructures.get(type(data), ...)) is ...:
            trace.exception(StructureTypeError(tuple(self.substructures.keys()), type(data), "Data"))
            return None
        return output

    def iter_structures(self) -> Sequence[Structure]:
        return [structure for structure in self.substructures.values() if structure is not None]

    def get_tag_paths_extra(self, data: Con[D], tag: StructureTag, data_path: DataPath, trace: Trace, environment: PrinterEnvironment) -> Sequence[DataPath]:
        tags = self.union_tags.get(type(data.data), None) # may not exist
        if tags is not None and tag in tags:
            return (data_path.copy(...).embed(data.data),)
        return ()

    def get_uses(self, data: Con[D], usage_tracker:UsageTracker, parent_use:Use|None, trace: Trace, environment: PrinterEnvironment) -> OrderedSet[Use]:
        if not usage_tracker.still_used(self): return OrderedSet(())
        with trace.enter(self, self.trace_name, data):
            output:OrderedSet[Use] = OrderedSet(())
            output.update(super().get_uses(data, usage_tracker, parent_use, trace, environment))
            for this_type in self.substructures.keys():
                if isinstance(data.data, this_type):
                    output.add(UnionStructureUse(this_type, self, usage_tracker, StructureUse(self, None, parent_use)))
                    break
            else: StructureTypeError(tuple(self.substructures.keys()), type(data.data), "Data")
            return output
        return OrderedSet(())

    def get_all_uses(self, memo:set[Structure], parent_use:Use|None) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        output:OrderedSet[Use] = OrderedSet(())
        output.update(super().get_all_uses(memo, parent_use))
        self_use = StructureUse(self, None, parent_use)
        for type, substructure in self.substructures.items():
            output.add(UnionStructureUse(type, self, None, self_use))
            if substructure is not None:
                output.update(substructure.get_all_uses(memo, self_use if substructure.is_inline else None))
        return output
