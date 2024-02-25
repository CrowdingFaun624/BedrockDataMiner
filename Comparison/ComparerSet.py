from typing import Generic, TYPE_CHECKING, TypeVar, Union

import Comparison.ComparisonUtilities as CU
import Comparison.Difference as D
import Comparison.Normalizer as Normalizer
import Comparison.Trace as Trace

if TYPE_CHECKING:
    import Comparison.ComparerSection as ComparerSection

d = TypeVar("d")

class ComparerSet(Generic[d]):
    '''Contains one or two ComparerSections. Is used internally.
    Is used for when a value is a Diff and must use two different printers.'''

    def __init__(self, comparers:dict[D.DiffType,"ComparerSection.ComparerSection"]) -> None:
        self.comparers = comparers

    def __repr__(self) -> str:
        return "<ComparerSet %s>" % self.comparers

    def __len__(self) -> int:
        return len(self.comparers)

    def __contains__(self, item:D.DiffType) -> bool:
        return item in self.comparers

    def __getitem__(self, key:D.DiffType|int) -> Union["ComparerSection.ComparerSection",None]:
        if isinstance(key, D.DiffType):
            return self.comparers[key]
        elif isinstance(key, int):
            return list(self.comparers.values())[key]
        else:
            raise KeyError("Attempted to index a ComparerSet using a %s rather than a D.DiffType!" % type(key))

    def print_text(self, key:D.DiffType|int, data:d, trace:Trace.Trace) -> list[str]:
        comparer = self[key]
        if comparer is None:
            return [CU.stringify(data)]
        else:
            return comparer.print_text(data, trace)

    def compare_text(self, key:D.DiffType|int, data:d, trace:Trace.Trace) -> tuple[list[str],bool]:
        comparer = self[key]
        if comparer is None:
            raise RuntimeError("Attempted to compare (key %s) using a NoneType object at %s!" % (key, trace))
        else:
            return comparer.compare_text(data, trace)

    def compare(self, data1:d, data2:d, trace:Trace.Trace) -> tuple[d,list[tuple[Trace.Trace,Exception]]]:
        if (len(self) == 1) or (len(self) == 2 and self[0] == self[1]):
            # both items have the same ComparerSection.
            comparer = self[0]
            if comparer is None:
                return D.Diff(data1, data2), []
            else:
                # items must be not equal because then the D.Diff could not be created.
                return comparer.compare(data1, data2, trace)
        else:
            # items have different data types.
            return D.Diff(data1, data2), []
