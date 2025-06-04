from typing import Sequence

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.Normalizer import Normalizer
from Structure.PassthroughStructure import PassthroughStructure
from Structure.Structure import Structure
from Structure.StructureEnvironment import PrinterEnvironment
from Utilities.Exceptions import StructureTypeError, SwitchStructureError
from Utilities.Trace import Trace


class SwitchStructure[D, BO, CO](PassthroughStructure[D, BO, CO]):

    __slots__ = (
        "switch_function",
        "switches",
        "types",
    )

    def link_switch_structure(
        self,
        switch_function:Normalizer,
        switches:dict[str,tuple[Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None, tuple[type,...]]],
    ) -> None:
        self.switch_function = switch_function
        self.switches = {key: structure for key, (structure, types) in switches.items()}
        self.types = {key: types for key, (structure, types) in switches.items()}

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
