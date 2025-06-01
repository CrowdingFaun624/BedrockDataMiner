from typing import Sequence

import Structure.Container as Con
import Structure.Difference as Diff
import Structure.Normalizer as Normalizer
import Structure.PassthroughStructure as PassthroughStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace


class SwitchStructure[D, BO, CO](PassthroughStructure.PassthroughStructure[D, BO, CO]):

    __slots__ = (
        "switch_function",
        "switches",
        "types",
    )

    def link_switch_structure(
        self,
        switch_function:Normalizer.Normalizer,
        switches:dict[str,tuple[Structure.Structure[D, Con.Con[D], Con.Don[D], Con.Don[D]|Diff.Diff[Con.Don[D]], BO, CO]|None, tuple[type,...]]],
    ) -> None:
        self.switch_function = switch_function
        self.switches = {key: structure for key, (structure, types) in switches.items()}
        self.types = {key: types for key, (structure, types) in switches.items()}

    def get_structure(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Structure.Structure[D, Con.Con[D], Con.Don[D], Con.Don[D]|Diff.Diff[Con.Don[D]], BO, CO]|None:
        switch_key:str = self.switch_function(data)
        structure = self.switches.get(switch_key, ...)
        if structure is ...:
            trace.exception(Exceptions.SwitchStructureError(switch_key, list(self.switches.keys()), self))
            return None
        return structure

    def iter_structures(self) -> Sequence[Structure.Structure]:
        return [structure for structure in self.switches.values() if structure is not None]

    def type_check_extra(self, data: Con.Con[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> None:
        switch_key:str = self.switch_function(data.data)
        types = self.types.get(switch_key, ...)
        if types is ...:
            trace.exception(Exceptions.SwitchStructureError(switch_key, list(self.switches.keys()), self))
            return None
        if not isinstance(data.data, types):
            trace.exception(Exceptions.StructureTypeError(types, type(data.data), "Data"))
