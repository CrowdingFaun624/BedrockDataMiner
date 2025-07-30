from types import EllipsisType
from typing import Container, Mapping, Sequence

from ordered_set import OrderedSet

import Domain.Domain as Domain
from Structure.Container import Con, Don
from Structure.DataPath import DataPath
from Structure.Difference import Diff
from Structure.SimilarityCache import SimilarityCache
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Structure.StructureInfo import StructureInfo
from Structure.StructureTag import StructureTag
from Structure.Uses import UsageTracker, Use
from Utilities.Trace import Trace
from Version.Version import Version


class Structure[A, B:Con, C:Don, D:Don|Diff, BO, CO]():
    '''
    Modular piece that compares and provides structured access to data.
    '''

    any_delegate_works: bool = False
    '''
    If True, InapplicableDelegateErrors won't be raised for this Structure type.
    '''

    __slots__ = (
        "children_has_garbage_collection",
        "children_tags",
        "domain",
        "full_name",
        "is_inline",
        "name",
        "trace_name",
    )

    def __init__(self, name:str, full_name:str, trace_name:str, is_inline:bool, domain:"Domain.Domain") -> None:
        self.name = name
        self.full_name = full_name
        self.trace_name = trace_name
        self.is_inline = is_inline
        self.domain = domain

    def link_structure(
        self,
        children_has_garbage_collection:bool,
        children_tags:set[StructureTag],
    ) -> None:
        self.children_has_garbage_collection = children_has_garbage_collection
        self.children_tags = children_tags

    def clear_similarity_cache(self, keep:Container[tuple[Version, StructureInfo]]) -> None:
        for similarity_cache in self.get_similarity_caches():
            similarity_cache.clear(keep)

    def get_substructure(self, data:B, trace:Trace, environment:PrinterEnvironment) -> tuple[Con,"Structure|None|EllipsisType"]:
        '''
        Returns the substructure for this data. Only defined for PassthroughStructure and WithinStructure. Used for `get_common_substructure`.
        Returns None for the second tuple item if there is a null-Structure; returns ... if the sub-Structure is not a PassthroughStructure or WithinStructure
        '''
        return data, ...

    def get_similarity_caches(self) -> Sequence["SimilarityCache"]:
        # implemented if the Structure type has a SimilarityCache.
        return ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.full_name}>"

    def __hash__(self) -> int:
        return id(self)

    def iter_structures(self) -> Sequence["Structure"]:
        return ()

    def get_descendants(self, memo:set["Structure"]) -> set["Structure"]:
        memo.add(self)
        for structure in self.iter_structures():
            if structure not in memo:
                structure.get_descendants(memo)
        return memo

    def containerize(self, data:A, trace:Trace, environment:PrinterEnvironment) -> B|EllipsisType:
        '''
        Converts the data into a containerized version.
        '''
        ...

    def diffize(self, data:B, bundle:tuple[int,...], trace:Trace, environment:ComparisonEnvironment) -> Mapping[tuple[int,...],C]|EllipsisType:
        '''
        Converts the containerized data into dontainerized data. Although the output may not be a Diff, it may contain Diffs.
        '''
        ...

    def type_check(self, data:B, trace:Trace, environment:PrinterEnvironment) -> None:
        '''
        Makes sure that the data relevant to this Structure has the correct types.
        '''
        ...

    def get_tag_paths(self, data:B, tag:StructureTag, data_path: DataPath, trace:Trace, environment:PrinterEnvironment) -> Sequence[DataPath]:
        '''
        Returns the DataPaths on which the given tag exists in the Structure for the given data..
        '''
        ...

    def get_uses(self, data:B, usage_tracker:UsageTracker, parent_use:Use|None, trace:Trace, environment:PrinterEnvironment) -> OrderedSet[Use]:
        '''
        Returns a set of Uses, all of which are used.
        '''
        ...

    def get_all_uses(self, memo:set["Structure"], parent_use:Use|None) -> OrderedSet[Use]:
        '''
        Returns all possible Uses.
        '''
        ...

    def compare(self, datas:tuple[tuple[int, B], ...], trace:Trace, environment:ComparisonEnvironment) -> tuple[D|EllipsisType, bool, bool]:
        '''
        Combines `datas` into a single object containing Diffs.
        Returns the combined data,
        if there are any changes detected, and
        if the combined data is or contains any Diffs with a `length` greater than 1.
        :datas: All data to be combined.
        '''
        ...

    def get_similarity(self, data1:B, data2:B, branch1:int, branch2:int, trace:Trace, environment:ComparisonEnvironment) -> tuple[float, bool]:
        '''
        Returns how similar two objects are, with 0 being no similarity and 1
        being equal. Also returns if the two objects are exactly the same (some
        situations in StringStructure can have this be different from
        similarity). If the boolean is True, then the float must be 1.0.
        '''
        ...

    def print_branch(self, data:B, trace:Trace, environment:PrinterEnvironment) -> BO|EllipsisType:
        '''
        Prints one branch of data. Returns an Ellipsis if there was an error.
        '''
        return ...

    def print_comparison(self, data:D, bundle:tuple[int,...], trace:Trace, environment:ComparisonEnvironment) -> CO|EllipsisType:
        '''
        Prints a comparison of data. Returns an Ellipsis if there was an error.
        '''
        return ...
