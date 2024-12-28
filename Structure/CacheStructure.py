from typing import TYPE_CHECKING, Any, Iterator, Union

import Component.Types as Types
import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.PassthroughStructure as PassthroughStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTag as StructureTag
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

if TYPE_CHECKING:
    import Structure.Delegate.Delegate as Delegate

class CacheStructure[d](PassthroughStructure.PassthroughStructure[d]):

    __slots__ = (
        "cache",
        "cache_check_all_types",
        "cache_compare",
        "cache_compare_text",
        "cache_get_referenced_files",
        "cache_get_similarity",
        "cache_get_tag_paths",
        "cache_normalize",
        "cache_print_text",
        "cache_remove_threshold",
        "searches",
    )

    def __init__(
            self,
            name:str,
            cache_remove_threshold:int,
            cache_check_all_types:bool,
            cache_normalize:bool,
            cache_get_tag_paths:bool,
            cache_get_referenced_files:bool,
            cache_compare_text:bool,
            cache_print_text:bool,
            cache_get_similarity:bool,
            cache_compare:bool,
            children_has_normalizer:bool,
            children_has_garbage_collection:bool,
        ) -> None:
        # CacheStructure overrides get_similarity, so max ancestor and descendent depth don't matter.
        super().__init__(name, None, None, children_has_normalizer, children_has_garbage_collection)

        self.searches:int = 0
        '''Increases each time `clear_old_items` is called.'''
        self.cache_remove_threshold = cache_remove_threshold
        '''How many consecutive times a cache item must be not retrieved for it to be removed.'''
        self.cache:dict[int,CacheItem[d]] = {}
        self.cache_check_all_types = cache_check_all_types
        self.cache_normalize = cache_normalize
        self.cache_get_tag_paths = cache_get_tag_paths
        self.cache_get_referenced_files = cache_get_referenced_files
        self.cache_compare_text = cache_compare_text
        self.cache_print_text = cache_print_text
        self.cache_get_similarity = cache_get_similarity
        self.cache_compare = cache_compare

    def link_substructures(
        self,
        structure:Structure.Structure[d]|None,
        delegate:Union["Delegate.Delegate", None],
        types:tuple[type,...],
        children_tags:set[StructureTag.StructureTag],
    ) -> None:
        super().link_substructures(structure, delegate, types, [], [], types, children_tags)

    def get_structure(self) -> Structure.Structure[d]:
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        return self.structure

    def check_all_types(self, data: d, environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        structure = self.get_structure()
        if not environment.should_cache or not self.cache_check_all_types:
            return structure.check_all_types(data, environment)
        data_hash = Types.hash_data(data)
        cache_item = self.cache.pop(data_hash, None)
        if cache_item is not None:
            self.cache[data_hash] = cache_item # the point of this is to move it to the front.
            cache_item.retrieve_index = self.searches
            if cache_item.check_all_types:
                return cache_item.get_check_all_types_data()
        else:
            new_cache_item:CacheItem[d] = CacheItem(self.delegate, self.searches)
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.check_all_types(data, environment)
        cache_item.set_check_all_types(output)
        return output

    def normalize(self, data:d, environment:StructureEnvironment.PrinterEnvironment) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        structure = self.get_structure()
        if not environment.structure_environment.should_cache or not self.cache_normalize:
            return structure.normalize(data, environment)
        data_hash = Types.hash_data(data)
        cache_item = self.cache.pop(data_hash, None)
        if cache_item is not None:
            self.cache[data_hash] = cache_item
            cache_item.retrieve_index = self.searches
            if cache_item.normalize:
                return cache_item.get_normalize_data()
        else:
            new_cache_item:CacheItem[d] = CacheItem(self.delegate, self.searches)
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.normalize(data, environment)
        cache_item.set_normalize((data, output[1]) if output[0] is None else output)
        # the data must be stored in the cache item because when the data is
        # being retrieved later, the substructure may have just returned None,
        # but none of the changes that the normalizer to that data were applied
        # to this data.
        return output

    def get_tag_paths(self, data:d, tag:StructureTag.StructureTag, data_path:DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        structure = self.get_structure()
        if not environment.should_cache or not self.cache_get_tag_paths:
            return structure.get_tag_paths(data, tag, data_path, environment)
        data_hash = Types.hash_data((data, tag))
        cache_item = self.cache.pop(data_hash, None)
        if cache_item is not None:
            self.cache[data_hash] = cache_item
            cache_item.retrieve_index = self.searches
            if cache_item.get_tag_paths:
                return cache_item.get_get_tag_paths_data()
        else:
            new_cache_item:CacheItem[d] = CacheItem(self.delegate, self.searches)
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.get_tag_paths(data, tag, data_path, environment)
        cache_item.set_get_tag_paths(output)
        return output

    def get_referenced_files(self, data: d, environment: StructureEnvironment.PrinterEnvironment) -> Iterator[int]:
        if not self.children_has_garbage_collection:
            return; yield
        structure = self.get_structure()
        if not environment.structure_environment.should_cache or not self.cache_get_referenced_files:
            yield from structure.get_referenced_files(data, environment)
        data_hash = Types.hash_data(data)
        cache_item = self.cache.pop(data_hash, None)
        if cache_item is not None:
            self.cache[data_hash] = cache_item
            cache_item.retrieve_index = self.searches
            if cache_item.get_referenced_files_data:
                yield from cache_item.get_get_referenced_files_data()
        else:
            new_cache_item:CacheItem[d] = CacheItem(self.delegate, self.searches)
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.get_referenced_files(data, environment)
        cache_item.set_get_referenced_files(output)
        yield from output

    def compare_text(self, data: d, environment:StructureEnvironment.ComparisonEnvironment) -> tuple[Any, bool, list[Trace.ErrorTrace]]:
        structure = self.get_structure()
        if not environment.structure_environment.should_cache or not self.cache_compare_text:
            return structure.compare_text(data, environment)
        data_hash = Types.hash_data(data)
        cache_item = self.cache.pop(data_hash, None)
        if cache_item is not None:
            self.cache[data_hash] = cache_item
            cache_item.retrieve_index = self.searches
            if cache_item.compare_text:
                return cache_item.get_compare_text_data(environment)
        else:
            new_cache_item:CacheItem[d] = CacheItem(self.delegate, self.searches)
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.compare_text(data, environment)
        cache_item.set_compare_text(output, environment)
        return output

    def print_text(self, data: d, environment:StructureEnvironment.PrinterEnvironment) -> tuple[Any, list[Trace.ErrorTrace]]:
        structure = self.get_structure()
        if not environment.structure_environment.should_cache or not self.cache_print_text:
            return structure.print_text(data, environment)
        data_hash = Types.hash_data(data)
        cache_item = self.cache.pop(data_hash, None)
        if cache_item is not None:
            self.cache[data_hash] = cache_item
            cache_item.retrieve_index = self.searches
            if cache_item.print_text:
                return cache_item.get_print_text_data(environment)
        else:
            new_cache_item:CacheItem[d] = CacheItem(self.delegate, self.searches)
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.print_text(data, environment)
        cache_item.set_print_text(output, environment)
        return output

    def get_similarity(self, data1: d, data2: d, depth:int, max_depth:int|None, environment:StructureEnvironment.ComparisonEnvironment, exceptions:list[Trace.ErrorTrace], branch:int) -> float:
        structure = self.get_structure()
        if not environment.structure_environment.should_cache or not self.cache_get_similarity:
            return structure.get_similarity(data1, data2, depth, max_depth, environment, exceptions, branch)
        data_hash = hash((Types.hash_data(data1), Types.hash_data(data2), depth, max_depth))
        cache_item = self.cache.pop(data_hash, None)
        if cache_item is not None:
            self.cache[data_hash] = cache_item
            cache_item.retrieve_index = self.searches
            if cache_item.get_similarity:
                return cache_item.get_get_similarity_data()
        else:
            new_cache_item:CacheItem[d] = CacheItem(self.delegate, self.searches)
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.get_similarity(data1, data2, depth, max_depth, environment, exceptions, branch)
        cache_item.set_get_similarity(output)
        return output

    def compare(self, data1: d, data2: d, environment:StructureEnvironment.ComparisonEnvironment, branch:int, branches:int) -> tuple[d|D.Diff[d], bool, list[Trace.ErrorTrace]]:
        structure = self.get_structure()
        if not environment.structure_environment.should_cache or not self.cache_compare:
            return structure.compare(data1, data2, environment, branch, branches)
        data_hash = hash((Types.hash_data(data1), Types.hash_data(data2)))
        cache_item = self.cache.pop(data_hash, None)
        if cache_item is not None:
            self.cache[data_hash] = cache_item
            cache_item.retrieve_index = self.searches
            if cache_item.compare:
                return cache_item.get_compare_data()
        else:
            new_cache_item:CacheItem[d] = CacheItem(self.delegate, self.searches)
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.compare(data1, data2, environment, branch, branches)
        cache_item.set_compare(output)
        return output

    def clear_old_items(self) -> None:
        '''
        Clears items that have not been accessed in too long.
        Be careful where you use this, since calling this function
        changes its future behavior.
        '''
        # this works because due to the popping and re-adding I do,
        # all of the cache items are sorted in the dict by their
        # retrieve index
        items_to_remove:list[int] = [] # cannot change size of dict while iterating.
        for data_hash, cache_item in self.cache.items():
            if self.searches - cache_item.retrieve_index >= self.cache_remove_threshold:
                items_to_remove.append(data_hash)
            else:
                break
        for item in items_to_remove:
            del self.cache[item]
        self.searches += 1

    def clear_cache(self) -> None:
        self.cache.clear()

class CacheItem[d]():

    __slots__ = (
        "cache_retrieve",
        "cache_store",
        "check_all_types",
        "check_all_types_data",
        "compare",
        "compare_data",
        "compare_text",
        "compare_text_data",
        "get_referenced_files",
        "get_referenced_files_data",
        "get_similarity",
        "get_similarity_data",
        "get_tag_paths",
        "get_tag_paths_data",
        "normalize",
        "normalize_data",
        "print_text",
        "print_text_data",
        "retrieve_index",
    )

    def __init__(self, delegate:Union["Delegate.Delegate", None], creation_index:int) -> None:
        self.cache_store = delegate.cache_store if delegate is not None else lambda data, environment: data
        self.cache_retrieve = delegate.cache_retrieve if delegate is not None else lambda data, environment: data
        self.retrieve_index = creation_index

        self.check_all_types = False
        self.check_all_types_data:list[Trace.ErrorTrace]|None = None
        self.normalize = False
        self.normalize_data:tuple[Any|None,list[Trace.ErrorTrace]]|None = None
        self.get_tag_paths = False
        self.get_tag_paths_data:tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]|None = None
        self.get_referenced_files = False
        self.get_referenced_files_data:list[int]|None = None
        self.compare_text = False
        self.compare_text_data:tuple[Any,bool,list[Trace.ErrorTrace]]|None = None
        self.print_text = False
        self.print_text_data:tuple[Any, list[Trace.ErrorTrace]]|None = None
        self.get_similarity = False
        self.get_similarity_data:float|None = None
        self.compare = False
        self.compare_data:tuple[d|D.Diff[d], bool, list[Trace.ErrorTrace]]|None = None

    def get_check_all_types_data(self) -> list[Trace.ErrorTrace]:
        if self.check_all_types_data is None:
            raise Exceptions.AttributeNoneError("check_all_types_data", self)
        return [trace.copy() for trace in self.check_all_types_data]

    def set_check_all_types(self, data:list[Trace.ErrorTrace]) -> None:
        self.check_all_types = True
        self.check_all_types_data = [trace.copy() for trace in data]

    def get_normalize_data(self) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        if self.normalize_data is None:
            raise Exceptions.AttributeNoneError("normalize_data", self)
        return self.normalize_data[0], [trace.copy() for trace in self.normalize_data[1]]

    def set_normalize(self, data:tuple[Any|None,list[Trace.ErrorTrace]]) -> None:
        self.normalize = True
        self.normalize_data = (data[0], [trace.copy() for trace in data[1]])

    def get_get_tag_paths_data(self) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        if self.get_tag_paths_data is None:
            raise Exceptions.AttributeNoneError("get_tag_paths_data", self)
        return self.get_tag_paths_data[0], [trace.copy() for trace in self.get_tag_paths_data[1]]

    def set_get_tag_paths(self, data:tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]) -> None:
        self.get_tag_paths = True
        self.get_tag_paths_data = (data[0], [trace.copy() for trace in data[1]])

    def get_get_referenced_files_data(self) -> Iterator[int]:
        if self.get_referenced_files_data is None:
            raise Exceptions.AttributeNoneError("get_referenced_files_data", self)
        yield from self.get_referenced_files_data

    def set_get_referenced_files(self, data:Iterator[int]) -> None:
        self.get_referenced_files = True
        self.get_referenced_files_data = list(set(data)) # remove duplicates, but keep fast iter speed.

    def get_get_similarity_data(self) -> float:
        if self.get_similarity_data is None:
            raise Exceptions.AttributeNoneError("get_similarity_data", self)
        return self.get_similarity_data

    def set_get_similarity(self, data:float) -> None:
        self.get_similarity = True
        self.get_similarity_data = data

    def get_compare_text_data(self, environment:StructureEnvironment.ComparisonEnvironment) -> tuple[Any,bool,list[Trace.ErrorTrace]]:
        if self.compare_text_data is None:
            raise Exceptions.AttributeNoneError("compare_text_data", self)
        return self.cache_retrieve(self.compare_text_data[0], environment), self.compare_text_data[1], [trace.copy() for trace in self.compare_text_data[2]]

    def set_compare_text(self, data:tuple[Any,bool,list[Trace.ErrorTrace]], environment:StructureEnvironment.ComparisonEnvironment) -> None:
        self.compare_text = True
        self.compare_text_data = (self.cache_store(data[0], environment), data[1], [trace.copy() for trace in data[2]])

    def get_print_text_data(self, environment:StructureEnvironment.PrinterEnvironment) -> tuple[Any, list[Trace.ErrorTrace]]:
        if self.print_text_data is None:
            raise Exceptions.AttributeNoneError("print_text_data", self)
        return self.cache_retrieve(self.print_text_data[0], environment), [trace.copy() for trace in self.print_text_data[1]]

    def set_print_text(self, data:tuple[Any, list[Trace.ErrorTrace]], environment:StructureEnvironment.PrinterEnvironment) -> None:
        self.print_text = True
        self.print_text_data = (self.cache_store(data[0], environment), [trace.copy() for trace in data[1]])

    def get_compare_data(self) -> tuple[d|D.Diff[d], bool, list[Trace.ErrorTrace]]:
        if self.compare_data is None:
            raise Exceptions.AttributeNoneError("compare_data", self)
        return self.compare_data[0], self.compare_data[1], [trace.copy() for trace in self.compare_data[2]]

    def set_compare(self, data:tuple[d|D.Diff[d], bool, list[Trace.ErrorTrace]]) -> None:
        self.compare = True
        self.compare_data = (data[0], data[1], [trace.copy() for trace in data[2]])
