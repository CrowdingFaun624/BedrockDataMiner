from types import EllipsisType
from typing import AbstractSet, Mapping, Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.DataPath import DataPath
from Structure.Difference import Diff
from Structure.Function import Function
from Structure.Key import Key
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


class SwitchStructure[D, BO, CO](PassthroughStructure[D, BO, CO, str]):

    __slots__ = (
        "keys",
        "switch_function",
        "switch_tags",
        "switches",
        "types",
    )

    def link_switch_structure(
        self,
        keys:Mapping[str,Key[D]],
        switch_function:Function,
    ) -> None:
        self.switch_function = switch_function
        self.keys = keys

    def finalize_switch_structure(self) -> None:
        for key in self.keys.values():
            key.finalize_key()
        self.switches:Mapping[str, Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None] = {key: value.structure for key, value in self.keys.items()}
        self.switch_tags:Mapping[str,AbstractSet[StructureTag]] = {key: value.tags for key, value in self.keys.items() if len(value.tags) > 0}
        self.types:Mapping[str,tuple[type,...]] = {key: value.types for key, value in self.keys.items()}
        del self.keys

    def get_structure(self, data: D, trace: Trace, environment: PrinterEnvironment) -> tuple[Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None, str|EllipsisType]:
        switch_key:str = self.switch_function(data)
        structure = self.switches.get(switch_key, ...)
        if structure is ...:
            trace.exception(SwitchStructureError(switch_key, list(self.switches.keys()), self))
            return None, switch_key
        return structure, switch_key

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
        tags = self.switch_tags.get(switch_key, None) # may not exist
        if tags is not None and tag in tags:
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
