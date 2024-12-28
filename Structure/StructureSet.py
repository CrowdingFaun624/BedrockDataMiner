from typing import TYPE_CHECKING, Any, Union

import Structure.Difference as D
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Structure as Structure
    import Structure.StructureEnvironment as StructureEnvironment

class StructureSet[d]():
    '''
    Is used when a value is a Diff and can be split between two different Structures.
    '''

    def __init__(self, structures:dict[tuple[int,...]|None,Union["Structure.Structure[d]",None]]) -> None:
        '''
        :structures: The dict of Structures to store in this StructureSet.
        '''
        self.structures = structures
        self.branches = {
            branch: branches
            for branches in structures.keys()
            if branches is not None
            for branch in branches
        }

    def __repr__(self) -> str:
        return "<StructureSet %s>" % self.structures

    def __len__(self) -> int:
        return len(self.structures)

    def __contains__(self, item:int|tuple[int,...]|None) -> bool:
        if item is None or isinstance(item, tuple):
            return item in self.structures
        else:
            return item in self.branches

    def __getitem__(self, key:int|tuple[int,...]|None) -> Union["Structure.Structure[d]",None]:
        '''
        Returns a Structure or None.

        :key: The branch to choose a Structure with.
        '''
        if key is None or isinstance(key, tuple):
            return self.structures[key]
        else:
            return self.structures[self.branches[key]]

    def get(self, key:int|tuple[int,...]|None) -> Union["Structure.Structure[d]",None]:
        '''
        Returns a Structure or None. If it does not exist, returns None.

        :key: The branch to choose a Structure with.
        '''
        if key is None or isinstance(key, tuple):
            return self.structures.get(key, None)
        else:
            branches = self.branches.get(key, None)
            if branches is None:
                return None
            return self.structures.get(branches, None)

    def print_text(self, key:int|None, data:d, environment:"StructureEnvironment.PrinterEnvironment") -> tuple[Any,list[Trace.ErrorTrace]]:
        '''
        Generates lines from the data using the Structure given by the key.

        :key: The DiffType or list-index to choose a Structure with.
        :data: The data containing no Diffs to print.
        :environment: The ComparisonEnvironment to use.
        '''
        if key not in self:
            return [], [] # to get to here there must be another exception anyways
        structure = self[key]
        if structure is None:
            output, exceptions = (str(data), []) if environment.default_delegate is None else environment.default_delegate.print_text(data, environment)
            return output, exceptions
        else:
            return structure.print_text(data, environment)

    def compare_text(self, key:int|None, data:d, environment:"StructureEnvironment.ComparisonEnvironment") -> tuple[Any, bool, list[Trace.ErrorTrace]]:
        '''
        Generates comparison lines from the data using the Structure given by the key.

        :key: The branch or list-index to choose a Structure with.
        :data: The data containing Diffs to compare.
        :environment: The ComparisonEnvironment to use.
        '''
        structure = self[key]
        if structure is None:
            raise Exceptions.CompareWithNoneError(self, key)
        else:
            return structure.compare_text(data, environment)

    def compare(self, data1:d, data2:d, environment:"StructureEnvironment.ComparisonEnvironment", branch:int, branches:int) -> tuple[d|D.Diff[d],bool,list[Trace.ErrorTrace]]:
        '''
        Compares data using the Structure given by internal conditions.

        :data1: The data from the oldest Version.
        :data2: The data from the newest Version.
        :environment: The ComparisonEnvironment to use.
        '''
        structure1 = self[branch]
        structure2 = self[branch+1]
        if structure1 is not None and structure1 is structure2:
            return structure1.compare(data1, data2, environment, branch, branches)
        else:
            return D.Diff(branches, {tuple(range(0,branch+1)): data1, (branch+1,): data2}), True, []
