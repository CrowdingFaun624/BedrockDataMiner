from typing import Iterable, Sequence

import Structure.Delegate.Delegate as Delegate
import Structure.Normalizer as Normalizer
import Structure.PassthroughStructure as PassthroughStructure
import Structure.Structure as Structure
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions


class SwitchStructure[d](PassthroughStructure.PassthroughStructure[d]):

    __slots__ = (
        "switch_function",
        "switches",
    )

    def link_substructures(
        self,
        switch_function:Normalizer.Normalizer[d,str],
        switches:dict[str,"Structure.Structure[d]|None"],
        delegate:Delegate.Delegate|None,
        types:tuple[type,...],
        normalizer:Sequence[Normalizer.Normalizer],
        post_normalizer:Sequence[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
        children_tags:set[StructureTag.StructureTag]
    ) -> None:
        super().link_substructures(delegate, types, normalizer, post_normalizer, pre_normalized_types, children_tags)
        self.switch_function = switch_function
        self.switches = switches

    def get_structure(self, key:None, value: d) -> tuple[Structure.Structure|None, Sequence[Trace.ErrorTrace]]:
        try:
            switch_key = self.switch_function(value)
        except Exception as e:
            return None, [Trace.ErrorTrace(e, self.name, None, value)]
        try:
            substructure = self.switches.get(switch_key, ...)
        except Exception as e:
            return None, [Trace.ErrorTrace(Exceptions.SwitchStructureError(switch_key, list(self.switches.keys()), self), self.name, None, value)]
        if substructure is ...:
            return None, [Trace.ErrorTrace(Exceptions.SwitchStructureError(switch_key, list(self.switches.keys()), self), self.name, None, value)]
        else:
            return substructure, ()

    def iter_structures(self) -> Iterable[Structure.Structure]:
        return (structure for structure in self.switches.values() if structure is not None)
