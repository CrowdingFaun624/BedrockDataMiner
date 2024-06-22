from typing import Any, Generic, TypeVar

import Structure.DataPath as DataPath
import Structure.Hashing as Hashing
import Structure.PassthroughStructure as PassthroughStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureUtilities as SU
import Structure.Trace as Trace
import Utilities.Exceptions as Exceptions

d = TypeVar("d")

class CacheStructure(PassthroughStructure.PassthroughStructure[d]):

    def __init__(
            self,
            name:str,
            cache_check_all_types:bool,
            cache_normalize:bool,
            cache_get_tag_paths:bool,
            cache_compare_text:bool,
            cache_print_text:bool,
            cache_compare:bool,
            children_has_normalizer:bool,
            children_tags:set[str]
        ) -> None:
        super().__init__(name, name, children_has_normalizer, children_tags)

        self.cache:dict[int,CacheItem[d]] = {}
        self.cache_check_all_types = cache_check_all_types
        self.cache_normalize = cache_normalize
        self.cache_get_tag_paths = cache_get_tag_paths
        self.cache_compare_text = cache_compare_text
        self.cache_print_text = cache_print_text
        self.cache_compare = cache_compare

        self.structure:Structure.Structure[d]|None = None
        self.types:tuple[type,...]|None = None

    def link_substructures(
        self,
        structure:Structure.Structure[d],
        types:list[type],
    ) -> None:
        super().link_substructures(structure, types, [])

    def get_structure(self) -> Structure.Structure:
        if self.structure is None:
            raise Exceptions.AttributeNoneError("structure", self)
        return self.structure

    def check_all_types(self, data: d, environment:StructureEnvironment.StructureEnvironment) -> list[Trace.ErrorTrace]:
        structure = self.get_structure()
        if not environment.should_cache or not self.cache_check_all_types:
            return structure.check_all_types(data, environment)
        data_hash = Hashing.hash_data(data)
        cache_item = self.cache.get(data_hash)
        if cache_item is not None and cache_item.check_all_types:
            return cache_item.get_check_all_types_data()
        if cache_item is None:
            new_cache_item:CacheItem[d] = CacheItem()
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.check_all_types(data, environment)
        cache_item.set_check_all_types(output)
        return output

    def normalize(self, data:d, environment:StructureEnvironment.StructureEnvironment) -> tuple[Any|None,list[Trace.ErrorTrace]]:
        structure = self.get_structure()
        if not environment.should_cache or not self.cache_normalize:
            return structure.normalize(data, environment)
        data_hash = Hashing.hash_data(data)
        cache_item = self.cache.get(data_hash)
        if cache_item is not None and cache_item.normalize:
            return cache_item.get_normalize_data()
        if cache_item is None:
            new_cache_item:CacheItem[d] = CacheItem()
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.normalize(data, environment)
        cache_item.set_normalize(output)
        return output

    def get_tag_paths(self, data:d, tag:str, data_path:DataPath.DataPath, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[DataPath.DataPath],list[Trace.ErrorTrace]]:
        structure = self.get_structure()
        if not environment.should_cache or not self.cache_get_tag_paths:
            return structure.get_tag_paths(data, tag, data_path, environment)
        data_hash = Hashing.hash_data(data)
        cache_item = self.cache.get(data_hash)
        if cache_item is not None and cache_item.get_tag_paths:
            return cache_item.get_get_tag_paths_data()
        if cache_item is None:
            new_cache_item:CacheItem[d] = CacheItem()
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.get_tag_paths(data, tag, data_path, environment)
        cache_item.set_get_tag_paths(output)
        return output

    def compare_text(self, data: d, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], bool, list[Trace.ErrorTrace]]:
        structure = self.get_structure()
        if not environment.should_cache or not self.cache_compare_text:
            return structure.compare_text(data, environment)
        data_hash = Hashing.hash_data(data)
        cache_item = self.cache.get(data_hash)
        if cache_item is not None and cache_item.compare_text:
            return cache_item.get_compare_text_data()
        if cache_item is None:
            new_cache_item:CacheItem[d] = CacheItem()
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.compare_text(data, environment)
        cache_item.set_compare_text(output)
        return output

    def print_text(self, data: d, environment:StructureEnvironment.StructureEnvironment) -> tuple[list[SU.Line], list[Trace.ErrorTrace]]:
        structure = self.get_structure()
        if environment.should_cache or not self.cache_print_text:
            return structure.print_text(data, environment)
        data_hash = Hashing.hash_data(data)
        cache_item = self.cache.get(data_hash)
        if cache_item is not None and cache_item.print_text:
            return cache_item.get_print_text_data()
        if cache_item is None:
            new_cache_item:CacheItem[d] = CacheItem()
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.print_text(data, environment)
        cache_item.set_print_text(output)
        return output

    def compare(self, data1: d, data2: d, environment:StructureEnvironment.StructureEnvironment) -> tuple[d, bool, list[Trace.ErrorTrace]]:
        structure = self.get_structure()
        if environment.should_cache or not self.cache_compare:
            return structure.compare(data1, data2, environment)
        data_hash = hash((Hashing.hash_data(data1), Hashing.hash_data(data2)))
        cache_item = self.cache.get(data_hash)
        if cache_item is not None and cache_item.compare:
            return cache_item.get_compare_data()
        if cache_item is None:
            new_cache_item:CacheItem[d] = CacheItem()
            self.cache[data_hash] = new_cache_item
            cache_item = new_cache_item

        output = structure.compare(data1, data2, environment)
        cache_item.set_compare(output)
        return output

    def clear_caches(self, memo:set[Structure.Structure]) -> None:
        super().clear_caches(memo)
        self.cache.clear()

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
        self.compare_text_indents:list[int]|None=None
        self.print_text = False
        self.print_text_data:tuple[list[SU.Line], list[Trace.ErrorTrace]]|None = None
        self.print_text_indents:list[int]|None=None
        self.compare = False
        self.compare_data:tuple[d, bool, list[Trace.ErrorTrace]]|None = None

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

    def get_compare_text_data(self) -> tuple[list[SU.Line],bool,list[Trace.ErrorTrace]]:
        if self.compare_text_data is None:
            raise Exceptions.AttributeNoneError("compare_text_data", self)
        if self.compare_text_indents is None:
            raise Exceptions.AttributeNoneError("compare_text_indents", self)
        for line, indents in zip(self.compare_text_data[0], self.compare_text_indents):
            line.set_indent(indents)
        return self.compare_text_data[0], self.compare_text_data[1], [trace.copy() for trace in self.compare_text_data[2]]

    def set_compare_text(self, data:tuple[list[SU.Line],bool,list[Trace.ErrorTrace]]) -> None:
        self.compare_text = True
        self.compare_text_data = (data[0], data[1], [trace.copy() for trace in data[2]])
        self.compare_text_indents = [line.indents for line in data[0]]

    def get_print_text_data(self) -> tuple[list[SU.Line], list[Trace.ErrorTrace]]:
        if self.print_text_data is None:
            raise Exceptions.AttributeNoneError("print_text_data", self)
        if self.print_text_indents is None:
            raise Exceptions.AttributeNoneError("print_text_indents", self)
        for line, indents in zip(self.print_text_data[0], self.print_text_indents):
            line.set_indent(indents)
        return self.print_text_data[0], [trace.copy() for trace in self.print_text_data[1]]

    def set_print_text(self, data:tuple[list[SU.Line], list[Trace.ErrorTrace]]) -> None:
        self.print_text = True
        self.print_text_data = (data[0], [trace.copy() for trace in data[1]])
        self.print_text_indents = [line.indents for line in data[0]]

    def get_compare_data(self) -> tuple[d, bool, list[Trace.ErrorTrace]]:
        if self.compare_data is None:
            raise Exceptions.AttributeNoneError("compare_data", self)
        return self.compare_data[0], self.compare_data[1], [trace.copy() for trace in self.compare_data[2]]

    def set_compare(self, data:tuple[d, bool, list[Trace.ErrorTrace]]) -> None:
        self.compare = True
        self.compare_data = (data[0], data[1], [trace.copy() for trace in data[2]])
