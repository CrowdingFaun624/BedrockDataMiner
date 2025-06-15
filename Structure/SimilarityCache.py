from collections import defaultdict
from typing import Container
from weakref import WeakKeyDictionary

from Structure.Container import Con
from Structure.StructureInfo import StructureInfo

DEFAULT_REMOVAL_THRESHOLD:int = 2
removal_threshold:int = DEFAULT_REMOVAL_THRESHOLD # modified by MemoryUsage
disabled:bool = False # modified by MemoryUsage

class SimilarityCache[A: Con]():

    __slots__ = (
        "cache",
        "index",
    )

    def __init__(self) -> None:
        # weird data structure because WeakRefs are weird and special.
        self.cache:dict[tuple[StructureInfo, StructureInfo], WeakKeyDictionary[A, WeakKeyDictionary[A, tuple[float, bool, int]]]]\
            = defaultdict(lambda: WeakKeyDictionary())
        self.index:int = 0

    def get(self, item1:A, item2:A, structure_info1:StructureInfo, structure_info2:StructureInfo) -> tuple[float, bool]|None:
        environment_cache = self.cache.get((structure_info1, structure_info2))
        if environment_cache is None:
            return None
        subcache = environment_cache.get(item1)
        if subcache is None:
            return None
        cached_item = subcache.pop(item2, None)
        if cached_item is None:
            return None
        similarity, identical, _ = cached_item
        return similarity, identical

    def set(self, similarity_tuple:tuple[float, bool], item1:A, item2:A, environment1:StructureInfo, environment2:StructureInfo) -> tuple[float, bool]:
        if disabled:
            return similarity_tuple
        environment_cache = self.cache[environment1, environment2]
        subcache = environment_cache.get(item1)
        if subcache is None:
            subcache = environment_cache[item1] = WeakKeyDictionary()
        similarity, identical = similarity_tuple
        subcache[item2] = (similarity, identical, self.index)
        return similarity_tuple

    def clear(self, keep:Container[StructureInfo]) -> None:
        '''
        Clears all environment caches that do not have both environments in `keep`.
        :keep: A Container of PrinterEnvironments to keep in the cache.
        '''
        removals:list[tuple[StructureInfo, StructureInfo]] = []
        cache = self.cache
        index = self.index
        for (environment1, environment2), environment_cache in cache.items():
            # environment_cache would have length 0 if all keys were garbage collected.
            if len(environment_cache) == 0 or environment1 not in keep and environment2 not in keep:
                removals.append((environment1, environment2))
                continue
            subremovals:list[A] = []
            for key1, subcache in environment_cache.items():
                subsubremovals:list[A] = []
                for key2, (_, _, last_index) in subcache.items():
                    if index - last_index >= removal_threshold:
                        subsubremovals.append(key2)
                for removal_item in subsubremovals:
                    subcache.pop(removal_item)
                if len(subcache) == 0:
                    subremovals.append(key1)
            for removal_item in subremovals:
                environment_cache.pop(removal_item)
        for removal_item in removals:
            cache.pop(removal_item)

    def clear_all(self) -> None:
        self.cache.clear()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} size {len(self.cache)}>"
