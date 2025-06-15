from types import EllipsisType
from typing import Container, Mapping, Sequence

from Structure.Container import Con, Don
from Structure.DataPath import DataPath
from Structure.Difference import Diff
from Structure.Normalizer import Normalizer
from Structure.SimilarityCache import SimilarityCache
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Structure.StructureInfo import StructureInfo
from Structure.StructureTag import StructureTag
from Utilities.Exceptions import NormalizerEllipsisError
from Utilities.Trace import Trace


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
        "children_has_normalizer",
        "children_tags",
        "full_name",
        "name",
    )

    def __init__(self, name:str, full_name:str) -> None:
        self.name = name
        self.full_name = full_name

    def link_structure(
        self,
        children_has_garbage_collection:bool,
        children_has_normalizer:bool,
        children_tags:set[StructureTag],
    ) -> None:
        self.children_has_garbage_collection = children_has_garbage_collection
        self.children_has_normalizer = children_has_normalizer
        self.children_tags = children_tags

    def clear_similarity_cache(self, keep:Container[StructureInfo]) -> None:
        for similarity_cache in self.get_similarity_caches():
            similarity_cache.clear(keep)

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

    def get_structure_chain_end(self, data:B, trace:Trace, environment:PrinterEnvironment) -> "Structure|None":
        '''
        Returns the Structure at the end of a chain of AbstractPassthroughStructures
        '''
        with trace.enter(self, self.name, data):
            return self

    def normalize(self, data:A, trace:Trace, environment:PrinterEnvironment) -> A|EllipsisType:
        '''
        Manipulates the data before type checking and comparing. Returns ... if the super-Structure does not need to
        deal with changing data.
        '''
        ...

    def normalizer_pass(self, normalizers:Sequence[Normalizer], data:A, trace:Trace, environment:PrinterEnvironment) -> tuple[A, bool]:
        data_identity_changed:bool = False
        for normalizer in normalizers:
            if not normalizer.filter_pass(environment.structure_info):
                continue
            normalizer_output = normalizer(data)
            if normalizer_output is ...:
                raise NormalizerEllipsisError(normalizer)
            if normalizer_output is not None:
                data_identity_changed = True
                data = normalizer_output
        return data, data_identity_changed

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

    def get_referenced_files(self, data:B, trace:Trace, environment:PrinterEnvironment) -> set[int]:
        '''
        Returns files contained by this Structure or a child Structure.
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
