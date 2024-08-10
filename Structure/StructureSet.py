from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

import Structure.Difference as D
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Structure as Structure
    import Structure.StructureEnvironment as StructureEnvironment

d = TypeVar("d")

class StructureSet(Generic[d]):
    '''
    Is used when a value is a Diff and can be split between two different Structures.
    '''

    def __init__(self, structures:dict[D.DiffType,Union["Structure.Structure",None]]) -> None:
        '''
        :structures: The dict of Structures to store in this StructureSet.
        '''
        self.structures = structures

    def __repr__(self) -> str:
        return "<StructureSet %s>" % self.structures

    def __len__(self) -> int:
        return len(self.structures)

    def __contains__(self, item:D.DiffType) -> bool:
        return item in self.structures

    def __getitem__(self, key:D.DiffType|int) -> Union["Structure.Structure",None]:
        '''
        Returns a Structure or None.
        :key: The DiffType or the list-index to choose a Structure with.
        '''
        if isinstance(key, D.DiffType):
            return self.structures[key]
        elif isinstance(key, int):
            return list(self.structures.values())[key]

    def print_text(self, key:D.DiffType|int, data:d, environment:"StructureEnvironment.ComparisonEnvironment") -> tuple[Any,list[Trace.ErrorTrace]]:
        '''
        Generates lines from the data using the Structure given by the key.
        :key: The DiffType or list-index to choose a Structure with.
        :data: The data containing no Diffs to print.
        :environment: The ComparisonEnvironment to use.
        '''
        if isinstance(key, D.DiffType) and key not in self:
            return [], [] # to get to here there must be another exception anyways
        structure = self[key]
        if structure is None:
            output, exceptions = (str(data), []) if environment.default_delegate is None else environment.default_delegate.print_text(data, environment)
            return output, exceptions
        else:
            return structure.print_text(data, environment)

    def compare_text(self, key:D.DiffType|int, data:d, environment:"StructureEnvironment.ComparisonEnvironment") -> tuple[Any, bool, list[Trace.ErrorTrace]]:
        '''
        Generates comparison lines from the data using the Structure given by the key.
        :key: The DiffType or list-index to choose a Structure with.
        :data: The data containing Diffs to compare.
        :environment: The ComparisonEnvironment to use.
        '''
        structure = self[key]
        if structure is None:
            raise Exceptions.CompareWithNoneError(self, key)
        else:
            return structure.compare_text(data, environment)

    def compare(self, data1:d, data2:d, environment:"StructureEnvironment.ComparisonEnvironment") -> tuple[d|D.Diff[d,d],bool,list[Trace.ErrorTrace]]:
        '''
        Compares data using the Structure given by internal conditions.
        :data1: The data from the oldest Version.
        :data2: The data from the newest Version.
        :environment: The ComparisonEnvironment to use.
        '''
        if (len(self) == 1) or (len(self) == 2 and self[0] == self[1]):
            # both items have the same Structure.
            structure = self[0]
            if structure is None:
                return D.Diff(data1, data2), True, []
            else:
                # items must be not equal because then the D.Diff could not be created.
                return structure.compare(data1, data2, environment)
        else:
            # items have different data types.
            return D.Diff(data1, data2), True, []
