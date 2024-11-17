from typing import TYPE_CHECKING, Any, Generic, Iterable, Iterator, TypeVar, Union

import Structure.DataPath as DataPath
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate
    import Structure.StructureEnvironment as StructureEnvironment

a = TypeVar("a")

class Structure(Generic[a]):
    "Modular piece that generates comparison reports of data."

    def __init__(self, name:str, children_has_normalizer:bool, children_has_garbage_collection:bool) -> None:
        '''
        :name: The name of the Structure.
        :field: The string used to describe data with.
        :children_has_normalizer: If this Structure or its descendants has a Normalizer.
        :children_tags: The tags that this Structure or its descendants have.
        '''
        self.name = name
        self.children_has_normalizer = children_has_normalizer
        self.children_has_garbage_collection = children_has_garbage_collection
        
        self.delegate:Union["Delegate.Delegate", None] = None
        self.children_tags:set[StructureTag.StructureTag]|None = None

    def link_substructures(
        self,
        delegate:Union["Delegate.Delegate", None],
        children_tags:set[StructureTag.StructureTag],
    ) -> None:
        self.delegate = delegate
        self.children_tags = children_tags

    def __repr__(self) -> str:
        return "<%s %s>" % (self.__class__.__name__, self.name)

    def __hash__(self) -> int:
        return id(self)

    def get_descendants(self, memo:set["Structure"]) -> Iterable["Structure"]:
        '''
        Returns this Structure and all of its descendents.
        :memo: The set of Structures already returned.
        '''
        if self not in memo:
            yield self
        for substructure in self.iter_structures():
            if substructure in memo:
                continue
            memo.add(self)
            yield from substructure.get_descendants(memo)

    def check_all_types(self, data:a, environment:"StructureEnvironment.StructureEnvironment") -> list[Trace.ErrorTrace]:
        '''
        Checks the types of the data using this Structure. Returns a list of ErrorTraces.
        :data: The data to check the types of.
        :environment: The StructureEnvironment to use.
        '''
        ...

    def compare_text(self, data:a, environment:"StructureEnvironment.ComparisonEnvironment") -> tuple[Any,bool,list[Trace.ErrorTrace]]:
        '''
        Generates lines from an object containing Diffs.
        Returns a list of Lines, if there were any changes, and a list of ErrorTraces.
        :data: The object containing Diffs.
        :environment: The ComparisonEnvironment to use.
        '''
        if self.delegate is None:
            raise Exceptions.AttributeNoneError("delegate", self)
        return self.delegate.compare_text(data, environment)

    def print_text(self, data:a, environment:"StructureEnvironment.PrinterEnvironment") -> tuple[Any,list[Trace.ErrorTrace]]:
        '''
        Generates lines from an object containing no Diffs.
        Returns a list of Lines and a list of ErrorTraces.
        :data: The object containing no Diffs.
        :environment: The ComparisonEnvironment to use.
        '''
        if self.delegate is None:
            raise Exceptions.AttributeNoneError("delegate", self)
        return self.delegate.print_text(data, environment)

    def normalize(self, data:a, environment:"StructureEnvironment.PrinterEnvironment") -> tuple[Any|None,list[Trace.ErrorTrace]]:
        '''
        Manipulates the data before comparison.
        Returns the normalized data and a list of list of ErrorTraces.
        :data: The data to manipulate.
        :environment: The PrinterEnvironment to use.
        '''
        ...

    def get_tag_paths(self, data:a, tag:StructureTag.StructureTag, data_path:DataPath.DataPath, environment:"StructureEnvironment.StructureEnvironment") -> tuple[list[DataPath.DataPath], list[Trace.ErrorTrace]]:
        '''
        Returns the DataPaths on which the given tag exists in the Structure for the given data and a list of ErrorTraces.
        :data: The data to get the tag paths from.
        :tag: The tag to search for.
        :data_path: The current path of data traversed through the Structures so far.
        :environment: The StructureEnvironment to use.
        '''
        ...

    def get_referenced_files(self, data:a, environment:"StructureEnvironment.PrinterEnvironment") -> Iterator[int]:
        '''
        Returns any Files within the data.
        :data: The data to search for Files.
        :environment: The PrinterEnvironment to use.
        '''
        ...

    def compare(self, data1:a, data2:a, environment:"StructureEnvironment.ComparisonEnvironment") -> tuple[a,bool,list[Trace.ErrorTrace]]:
        '''
        Combines the data into a single object with Diffs in it. Returns the combined object and if there are any differences.
        :data1: The data from the oldest Version.
        :data2: The data from the newest Version.
        :environment: The ComparisonEnvironment to use.
        '''
        ...

    def get_similarity(self, data1:a, data2:a, depth:int, max_depth:int|None, environment:"StructureEnvironment.ComparisonEnvironment", exceptions:list[Trace.ErrorTrace]) -> float:
        '''
        Returns the similarity of data1 to data2. Is at most the greater of the complexities of the data.
        :data1: The data from the oldest Version.
        :data2: The data from the newest Version.
        :depth: The current count of get_similarity calls right now.
        :max_depth: The maximum depth before simple equality checks are used.
        :environment: The ComparisonEnvironment to use.
        '''
        ...

    def iter_structures(self) -> Iterable["Structure"]:
        '''Returns an Iterable of this Structure's substructures.'''
        ...
