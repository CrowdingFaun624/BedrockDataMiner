from typing import Any, Callable, Generic, Iterable, TypeVar

import Structure.DataPath as DataPath
import Structure.Difference as D
import Structure.Normalizer as Normalizer
import Structure.Structure as Structure
import Structure.StructureUtilities as SU
import Structure.Trace as Trace

a = TypeVar("a")
d = TypeVar("d")

class CacheStructure(Structure.Structure[d]):

    def __init__(
            self,
            name:str,
            structure:Structure.Structure[d]|None,
            types:tuple[type,...]|None,
            cache_check_all_types:bool,
            cache_normalize:bool,
            cache_get_tag_paths:bool,
            cache_compare_text:bool,
            cache_print_text:bool,
            cache_compare:bool,
            children_has_normalizer:bool,
            children_tags:set[str]
        ) -> None:
        super().__init__(name, name, None, children_has_normalizer, children_tags)

        self.types = types
        self.structure = structure
        self.cache:dict[int,CacheItem[d]] = {}
        self.cache_check_all_types = cache_check_all_types
        self.cache_normalize = cache_normalize
        self.cache_get_tag_paths = cache_get_tag_paths
        self.cache_compare_text = cache_compare_text
        self.cache_print_text = cache_print_text
        self.cache_compare = cache_compare

    def choose_structure_flat(self, key, value_type:type, value) -> Structure.Structure|None:
        return self.structure

    def check_all_types(self, data: d) -> list[Trace.ErrorTrace]:
        if not self.cache_check_all_types:
            assert self.structure is not None
            return self.structure.check_all_types(data)
        data_hash = hash_data(data)
        cache_item = self.cache.get(data_hash)
        if cache_item is not None and cache_item.check_all_types:
            assert cache_item.check_all_types_data is not None
            return cache_item.check_all_types_data
        if cache_item is None:
            new_cache_item:CacheItem[d] = CacheItem()
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        assert self.structure is not None
        output = self.structure.check_all_types(data)
        cache_item.set_check_all_types(output)
        return output

    def normalize(self, data:d, normalizer_dependencies:Normalizer.LocalNormalizerDependencies, version_number:int) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        if not self.cache_normalize:
            assert self.structure is not None
            return self.structure.normalize(data, normalizer_dependencies, version_number)
        data_hash = hash_data(data)
        cache_item = self.cache.get(data_hash)
        if cache_item is not None and cache_item.normalize:
            assert cache_item.normalize_data is not None
            return cache_item.normalize_data
        if cache_item is None:
            new_cache_item:CacheItem[d] = CacheItem()
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        assert self.structure is not None
        output = self.structure.normalize(data, normalizer_dependencies, version_number)
        cache_item.set_normalize(output)
        return output

    def get_tag_paths(self, data:d, tag:str, data_path:DataPath.DataPath) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        if not self.cache_get_tag_paths:
            assert self.structure is not None
            return self.structure.get_tag_paths(data, tag, data_path)
        data_hash = hash_data(data)
        cache_item = self.cache.get(data_hash)
        if cache_item is not None and cache_item.get_tag_paths:
            assert cache_item.get_tag_paths_data is not None
            return cache_item.get_tag_paths_data
        if cache_item is None:
            new_cache_item:CacheItem[d] = CacheItem()
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        assert self.structure is not None
        output = self.structure.get_tag_paths(data, tag, data_path)
        cache_item.set_get_tag_paths(output)
        return output

    def compare_text(self, data: d) -> tuple[list[SU.Line], bool, list[Trace.ErrorTrace]]:
        if not self.cache_compare_text:
            assert self.structure is not None
            return self.structure.compare_text(data)
        data_hash = hash_data(data)
        cache_item = self.cache.get(data_hash)
        if cache_item is not None and cache_item.compare_text:
            assert cache_item.compare_text_data is not None
            return cache_item.compare_text_data
        if cache_item is None:
            new_cache_item:CacheItem[d] = CacheItem()
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        assert self.structure is not None
        output = self.structure.compare_text(data)
        cache_item.set_compare_text(output)
        return output

    def print_text(self, data: d) -> tuple[list[SU.Line], list[Trace.ErrorTrace]]:
        if not self.cache_print_text:
            assert self.structure is not None
            return self.structure.print_text(data)
        data_hash = hash_data(data)
        cache_item = self.cache.get(data_hash)
        if cache_item is not None and cache_item.print_text:
            assert cache_item.print_text_data is not None
            return cache_item.print_text_data
        if cache_item is None:
            new_cache_item:CacheItem[d] = CacheItem()
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        assert self.structure is not None
        output = self.structure.print_text(data)
        cache_item.set_print_text(output)
        return output

    def compare(self, data1: d, data2: d) -> tuple[d, bool, list[Trace.ErrorTrace]]:
        if not self.cache_compare:
            assert self.structure is not None
            return self.structure.compare(data1, data2)
        data_hash = hash((hash_data(data1), hash_data(data2)))
        cache_item = self.cache.get(data_hash)
        if cache_item is not None and cache_item.compare:
            assert cache_item.compare_data is not None
            return cache_item.compare_data
        if cache_item is None:
            new_cache_item:CacheItem[d] = CacheItem()
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        assert self.structure is not None
        output = self.structure.compare(data1, data2)
        cache_item.set_compare(output)
        return output

    def clear_caches(self) -> None:
        super().clear_caches()
        self.cache.clear()

    def iter_structures(self) -> Iterable[Structure.Structure]:
        if self.structure is None:
            return []
        else:
            return [self.structure]

class CacheItem(Generic[d]):

    def __init__(self) -> None:
        self.check_all_types = False
        self.check_all_types_data:list[Trace.ErrorTrace]|None = None
        self.normalize = False
        self.normalize_data:tuple[Any|None,list[Trace.ErrorTrace]]|None = None
        self.get_tag_paths = False
        self.get_tag_paths_data:tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]|None = None
        self.compare_text = False
        self.compare_text_data:tuple[list[SU.Line],bool,list[Trace.ErrorTrace]]|None = None
        self.print_text = False
        self.print_text_data:tuple[list[SU.Line], list[Trace.ErrorTrace]]|None = None
        self.compare = False
        self.compare_data:tuple[d, bool, list[Trace.ErrorTrace]]|None = None

    def set_check_all_types(self, data:list[Trace.ErrorTrace]) -> None:
        self.check_all_types = True
        self.check_all_types_data = data

    def set_normalize(self, data:tuple[Any|None,list[Trace.ErrorTrace]]) -> None:
        self.normalize = True
        self.normalize_data = data

    def set_get_tag_paths(self, data:tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]) -> None:
        self.get_tag_paths = True
        self.get_tag_paths_data = data

    def set_compare_text(self, data:tuple[list[SU.Line],bool,list[Trace.ErrorTrace]]) -> None:
        self.compare_text = True
        self.compare_text_data = data

    def set_print_text(self, data:tuple[list[SU.Line], list[Trace.ErrorTrace]]) -> None:
        self.print_text = True
        self.print_text_data = data

    def set_compare(self, data:tuple[d, bool, list[Trace.ErrorTrace]]) -> None:
        self.compare = True
        self.compare_data = data

def hash_data(data:Any) -> int:
    '''
    Tries its best to hash anything, including mutable objects. Will throw an exception if it can't figure out how.
    :data: The data to hash
    '''
    default_hash_function:Callable[[Any],int]|None = getattr(data, "__hash__", None)
    if default_hash_function is not None:
        return default_hash_function(data)
    items_function:Callable[[Any],list[tuple[Any,Any]]]|None = getattr(data, "items", None)
    if items_function is not None:
        return hash(tuple((hash_data(key), hash_data(value)) for key, value in items_function(data)))
    iter_function:Callable[[Any],list[Any]]|None = getattr(data, "__iter__", None)
    if iter_function is not None:
        return hash(tuple(hash_data(item) for item in iter_function(data)))
    if isinstance(data, D.Diff):
        return hash((hash_data(data.old), hash_data(data.new)))
    raise TypeError("Cannot hash data with type %s!" % (data.__class__.__name__))
