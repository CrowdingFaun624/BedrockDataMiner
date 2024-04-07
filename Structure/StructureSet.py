from typing import Generic, TYPE_CHECKING, TypeVar, Union

import Structure.Difference as D
import Structure.StructureUtilities as SU
import Structure.Trace as Trace

if TYPE_CHECKING:
    import Structure.Structure as Structure

d = TypeVar("d")

class StructureSet(Generic[d]):
    '''Contains one or two Structures. Is used internally.
    Is used for when a value is a Diff and must use two different printers.'''

    def __init__(self, structures:dict[D.DiffType,Union["Structure.Structure",None]]) -> None:
        self.structures = structures

    def __repr__(self) -> str:
        return "<StructureSet %s>" % self.structures

    def __len__(self) -> int:
        return len(self.structures)

    def __contains__(self, item:D.DiffType) -> bool:
        return item in self.structures

    def __getitem__(self, key:D.DiffType|int) -> Union["Structure.Structure",None]:
        if isinstance(key, D.DiffType):
            return self.structures[key]
        elif isinstance(key, int):
            return list(self.structures.values())[key]
        else:
            raise KeyError("Attempted to index a StructureSet using a %s rather than a D.DiffType!" % type(key))

    def print_text(self, key:D.DiffType|int, data:d, trace:Trace.Trace) -> list[SU.Line]:
        if  isinstance(key, D.DiffType) and key not in self:
            raise RuntimeError("KeyError on \"%s\" in %s for data %s!" % (key, trace, data))
        structure = self[key]
        if structure is None:
            return [SU.Line(SU.stringify(data))]
        else:
            return structure.print_text(data, trace)

    def compare_text(self, key:D.DiffType|int, data:d, trace:Trace.Trace) -> tuple[list[SU.Line],bool]:
        structure = self[key]
        if structure is None:
            raise RuntimeError("Attempted to compare (key %s) using a NoneType object at %s!" % (key, trace))
        else:
            return structure.compare_text(data, trace)

    def compare(self, data1:d, data2:d, trace:Trace.Trace) -> tuple[d|D.Diff[d,d],list[tuple[Trace.Trace,Exception]]]:
        if (len(self) == 1) or (len(self) == 2 and self[0] == self[1]):
            # both items have the same Structure.
            structure = self[0]
            if structure is None:
                return D.Diff(data1, data2), []
            else:
                # items must be not equal because then the D.Diff could not be created.
                return structure.compare(data1, data2, trace)
        else:
            # items have different data types.
            return D.Diff(data1, data2), []
