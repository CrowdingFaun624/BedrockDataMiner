from typing import Any, Generic, TypeVar, cast

import Structure.ObjectStructure as ObjectStructure
import Structure.PrimitiveStructure as PrimitiveStructure
import Structure.Structure as Structure
import Structure.StructureBase as StructureBase
import Structure.StructureEnvironment as StructureEnvironment
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions
import Utilities.TypeVerifier.TypeVerifier as TypeVerifier

a = TypeVar("a")
'''
The output of this Delegate.
'''
b = TypeVar("b", bound=Structure.Structure|StructureBase.StructureBase)
'''
The Structure types this Delegate works on.
'''
c = TypeVar("c")
'''
The data that is stored in CacheStructures with this Delegate.
'''

class Delegate(Generic[a, b, c]):
    '''
    Object for displaying the output of Structures in different ways.
    Delegates are a Generic of three TypeVars.
    The first TypeVar (`a`) is the output of this Delegate.
    The second TypeVar (`b`) is the Structure types this Delegate works on. It can be a subclass of Structure or StructureBase.
    The third TypeVar (`c`) is the data that is stored in CacheStructures with this Delegate.
    '''

    type_verifier:TypeVerifier.TypeVerifier|None = None
    '''
    TypeVerifier used to verify the parameters of this Delegate.
    If not present, will use the function signature of `__init__`.
    '''

    key_type_verifier:TypeVerifier.TypeVerifier|None = None
    '''
    TypeVerifier used to verify each value in `keys` of this Delegate.
    If not present, no checking is done for `keys`.
    '''

    applies_to:tuple[type[StructureBase.StructureBase]|type[Structure.Structure]|type[None],...] = (StructureBase.StructureBase, ObjectStructure.ObjectStructure, PrimitiveStructure.PrimitiveStructure, type(None))

    def __init__(self, structure:b|None, keys:dict[str,Any]) -> None:
        '''
        :structure: The Structure that this Delegate belongs to. Can only be None if it is used as the default delegate of a StructureBase.
        :keys: Dictionary containing arguments from each key of a Keymap. If it's not a Keymap, the values of the keys dictionary will be empty.
        '''
        self.structure = structure

    def finalize(self) -> None:
        '''
        Runs during the finalize Component import phase.
        '''

    def get_structure(self) -> b:
        '''
        Returns the Structure associated with this Delegate.
        Raises an AttributeNoneError if it is None.
        '''
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        return self.structure

    def __repr__(self) -> str:
        if self.structure is None:
            return "<%s; no Structure>" % (self.__class__.__name__,)
        else:
            return "<%s of %s %s>" % (self.__class__.__name__, self.structure.__class__.__name__, self.structure.name)

    def cache_store(self, data:a, environment:StructureEnvironment.ComparisonEnvironment|StructureEnvironment.PrinterEnvironment) -> c:
        '''
        Returns data that is stored in a CacheStructure.
        When the data is retrieved, `cache_retrieve` is called.
        :data: Data of the same type that is returned by `compare_text` and `print_text`.
        :environment: The ComparisonEnvironment to use.
        '''
        return cast(c, data)

    def cache_retrieve(self, data:c, environment:StructureEnvironment.ComparisonEnvironment|StructureEnvironment.PrinterEnvironment) -> a:
        '''
        Given the data that was stored by `cache_store`,
        returns the original data.
        :data: The data stored in the cache that is returned by `cache_store`.
        :environment: The ComparisonEnvironment to use.
        '''
        return cast(a, data)

    def compare_text(self, data:Any, environment:StructureEnvironment.ComparisonEnvironment) -> tuple[a, bool, list[Trace.ErrorTrace]]:
        ...

    def print_text(self, data:Any, environment:StructureEnvironment.PrinterEnvironment) -> tuple[a, list[Trace.ErrorTrace]]:
        ...
