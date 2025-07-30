from typing import Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.DataPath import DataPath
from Structure.Difference import Diff
from Structure.Function import Function
from Structure.PassthroughStructure import PassthroughStructure
from Structure.Structure import Structure
from Structure.StructureEnvironment import PrinterEnvironment
from Structure.StructureTag import StructureTag
from Structure.Uses import (
    Region,
    StructureUse,
    SwitchStructureUse,
    TypeUse,
    UsageTracker,
    Use,
)
from Utilities.Exceptions import StructureTypeError, SwitchStructureError
from Utilities.Trace import Trace


class SwitchStructure[D, BO, CO](PassthroughStructure[D, BO, CO]):

    __slots__ = (
        "switch_function",
        "switch_tags",
        "switches",
        "types",
    )

    def link_switch_structure(
        self,
        switch_function:Function,
        structures:dict[str,Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None],
        tags:dict[str,set[StructureTag]],
        types:dict[str,tuple[type,...]],
    ) -> None:
        self.switch_function = switch_function
        self.switches = structures
        self.types = types
        self.switch_tags = tags

    def get_structure(self, data: D, trace: Trace, environment: PrinterEnvironment) -> Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None:
        switch_key:str = self.switch_function(data)
        structure = self.switches.get(switch_key, ...)
        if structure is ...:
            trace.exception(SwitchStructureError(switch_key, list(self.switches.keys()), self))
            return None
        return structure

    def iter_structures(self) -> Sequence[Structure]:
        return [structure for structure in self.switches.values() if structure is not None]

    def type_check_extra(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> None:
        switch_key:str = self.switch_function(data.data)
        types = self.types.get(switch_key, ...)
        if types is ...:
            trace.exception(SwitchStructureError(switch_key, list(self.switches.keys()), self))
            return None
        if not isinstance(data.data, types):
            trace.exception(StructureTypeError(types, type(data.data), "Data"))

    def get_tag_paths_extra(self, data: Con[D], tag: StructureTag, data_path: DataPath, trace: Trace, environment: PrinterEnvironment) -> Sequence[DataPath]:
        switch_key:str = self.switch_function(data)
        tags = self.switch_tags.get(switch_key, set()) # may not exist
        if tag in tags:
            return (data_path.copy(...).embed(data.data),)
        return ()

    def get_uses(self, data: Con[D], usage_tracker:UsageTracker, parent_use:Use|None, trace: Trace, environment: PrinterEnvironment) -> OrderedSet[Use]:
        if not usage_tracker.still_used(self): return OrderedSet(())
        with trace.enter(self, self.trace_name, ...):
            output:OrderedSet[Use] = OrderedSet(())
            output.update(super().get_uses(data, usage_tracker, parent_use, trace, environment))
            switch_key = self.switch_function(data.data)
            switch_structure_use = SwitchStructureUse(switch_key, self, usage_tracker, StructureUse(self, None, parent_use))
            output.add(switch_structure_use)
            for this_type in self.types[switch_key]:
                if isinstance(data.data, this_type):
                    output.add(TypeUse(this_type, Region.this_types, switch_structure_use, usage_tracker))
                    break
            else: raise StructureTypeError(self.types[switch_key], type(data.data), "Data")
            return output
        return OrderedSet(())

    def get_all_uses(self, memo: set[Structure], parent_use:Use|None) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        output:OrderedSet[Use] = OrderedSet(())
        output.update(super().get_all_uses(memo, parent_use))
        self_use = StructureUse(self, None, parent_use)
        for (switch_key, structure), (switch_key, types) in zip(self.switches.items(), self.types.items(), strict=True):
            if structure is not None:
                output.update(structure.get_all_uses(memo, self_use if structure.is_inline else None))
            switch_structure_use = SwitchStructureUse(switch_key, self, None, self_use)
            output.add(switch_structure_use)
            for type in types:
                output.add(TypeUse(type, Region.this_types, switch_structure_use, None))
        return OrderedSet(())
