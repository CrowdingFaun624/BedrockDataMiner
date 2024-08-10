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

    def choose_structure(self, key:Any, value:Any|D.Diff[Any,Any]) -> tuple[StructureSet.StructureSet, list[Trace.ErrorTrace]]:
        '''
        Returns a StructureSet of this Structure's substructure(s).
        '''
        exceptions:list[Trace.ErrorTrace] = []
        if isinstance(value, D.Diff):
            output:dict[D.DiffType,Structure.Structure|None] = {}
            if value.old is not D.NoExist:
                structure, new_exceptions = self.get_structure(key, value.old)
                exceptions.extend(exception.add(self.name, key) for exception in exceptions)
                output[D.DiffType.old] = structure
            if value.new is not D.NoExist:
                structure, new_exceptions = self.get_structure(key, value.new)
                exceptions.extend(exception.add(self.name, key) for exception in exceptions)
                output[D.DiffType.new] = structure
            return StructureSet.StructureSet(output), exceptions
        else:
            structure, new_exceptions = self.get_structure(key, value)
            exceptions.extend(exception.add(self.name, key) for exception in new_exceptions)
            return StructureSet.StructureSet({D.DiffType.not_diff: structure}), exceptions
