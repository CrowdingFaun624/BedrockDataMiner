from typing import Any, TypeVar

import Structure.Difference as D
import Structure.Structure as Structure
import Structure.StructureSet as StructureSet
import Structure.Trace as Trace

d = TypeVar("d")

class ObjectStructure(Structure.Structure[d]):
    '''
    Opposite of a PrimitiveStructure.
    Must have a substructure.
    '''

    def get_structure(self, key:Any, value:Any) -> tuple[Structure.Structure|None, list[Trace.ErrorTrace]]:
        '''
        Returns the substructure of this Structure.
        '''
        ...

    def choose_structure(self, key:Any, value:Any|D.Diff[Any]) -> tuple[StructureSet.StructureSet[d], list[Trace.ErrorTrace]]:
        '''
        Returns a StructureSet of this Structure's substructure(s).
        '''
        output:dict[tuple[int,...]|None,Structure.Structure|None] = {}
        exceptions:list[Trace.ErrorTrace] = []
        for branch, value_iter in D.iter_diff(value):
            structure, new_exceptions = self.get_structure(key, value_iter)
            exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
            output[branch] = structure
        return StructureSet.StructureSet(output), exceptions
