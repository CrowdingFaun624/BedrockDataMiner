from types import EllipsisType
from typing import Any, cast

import Domain.Domain as Domain
from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.Structure import Structure
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Utilities.Trace import Trace
from Utilities.TypeVerifier import TypeVerifier


class Delegate[DC:Con, DD:Don|Diff, S:Structure|None, BO, BC, CO, CC]():
    '''
    Object for displaying the output of Structures in different ways.
    Delegates are a Generic of seven TypeVars.\n
    The first TypeVar (`DC`) is the containerized data that is the input of `print_branch`.\n
    The second TypeVar (`DD`) is the compared data that is the input of `compare_text`.\n
    The third TypeVar (`S`) is the Structure types this Delegate works on.\n
    The fourth TypeVar (`BO`) is the output of `print_branch`.\n
    The fifth TypeVar (`BC`) is the data from `print_branch` that is stored in CacheStructures.\n
    The sixth TypeVar (`CO`) is the output of `print_comparison`.\n
    The seventh TypeVar (`CC`) is the data from `print_comparison` that is stored in CacheStructures.\n
    '''

    type_verifier:TypeVerifier|None = None
    '''
    TypeVerifier used to verify the parameters of this Delegate.
    If not present, will use the function signature of `__init__`.
    '''

    key_type_verifier:TypeVerifier|None = None
    '''
    TypeVerifier used to verify each value in `keys` of this Delegate.
    If not present, no checking is done for `keys`.
    '''

    uses_versions:bool = False
    '''
    True if this Delegate uses the Versions in any environments. Used for caching
    '''

    applies_to:tuple[type[Structure]|type[None],...] = (Structure, type(None))

    __slots__ = (
        "structure",
    )

    def __init__(self, structure:S, keys:dict[str,Any]) -> None:
        '''
        :structure: The Structure that this Delegate belongs to. Can only be None if it is used as the default delegate of a StructureBase.
        :keys: Dictionary containing arguments from each key of a Keymap. If it's not a Keymap, the values of the keys dictionary will be empty.
        '''
        self.structure = structure

    def finalize(self, domain:"Domain.Domain", trace:Trace) -> None:
        '''
        Runs during the finalize Component import phase.
        '''
        pass

    def __repr__(self) -> str:
        if self.structure is None:
            return f"<{self.__class__.__name__}; no Structure>"
        else:
            return f"<{self.__class__.__name__} of {self.structure.__class__.__name__} {self.structure.name}>"

    def cache_store_branch(self, data:BO, trace:Trace, environment:PrinterEnvironment) -> BC:
        '''
        Returns data from `print_branch` that is stored in a CacheStructure.
        When the data is retrieved, `cache_store_branch` is called.
        :data: Data of the same type that is returned by `print_branch`.
        :environment: The PrinterEnvironment to use.
        '''
        return cast(BC, data)

    def cache_retrieve_branch(self, data:BC, trace:Trace, environment:PrinterEnvironment) -> BO:
        '''
        Given the data that was stored by `cache_store_branch`, returns the original data.
        :Data: The data stored in the cache that is returned by `cache_store_branch`.
        :environment: The PrinterEnvironment to use.
        '''
        return cast(BO, data)

    def cache_store_comparison(self, data:CO, bundle:tuple[int,...], trace:Trace, environment:ComparisonEnvironment) -> CC:
        '''
        Returns data from `print_comparison` that is stored in a CacheStructure.
        When the data is retrieved, `cache_retrieve_comparison` is called.
        :data: Data of the same type that is returned by `print_comparison`.
        :environment: The ComparisonEnvironment to use.
        '''
        return cast(CC, data)

    def cache_retrieve_comparison(self, data:CC, bundle:tuple[int,...], trace:Trace, environment:ComparisonEnvironment) -> CO:
        '''
        Given the data that was stored by `cache_store_comparison`, returns the original data.
        :data: The data stored in the cache that is returned by `cache_store_comparison`.
        :environment: The ComparisonEnvironment to use.
        '''
        return cast(CO, data)

    def print_branch(self, data:DC, trace:Trace, environment:PrinterEnvironment) -> BO|EllipsisType:
        ...

    def print_comparison(self, data:DD, bundle:tuple[int,...], trace:Trace, environment:ComparisonEnvironment) -> CO|EllipsisType:
        ...
