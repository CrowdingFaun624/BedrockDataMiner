from collections import defaultdict
from typing import Container
from weakref import WeakKeyDictionary

import Structure.Container as Con
import Structure.StructureInfo as StructureInfo


class SimilarityCache[A: Con.Con]():
    
    def __init__(self) -> None:
        # weird data structure because WeakRefs are weird and special.
        self.cache:dict[tuple[StructureInfo.StructureInfo, StructureInfo.StructureInfo], WeakKeyDictionary[A, WeakKeyDictionary[A, tuple[float, bool]]]]\
            = defaultdict(lambda: WeakKeyDictionary())

    def get(self, item1:A, item2:A, structure_info1:StructureInfo.StructureInfo, structure_info2:StructureInfo.StructureInfo) -> tuple[float, bool]|None:
        environment_cache = self.cache.get((structure_info1, structure_info2))
        if environment_cache is None:
            return None
        subcache = environment_cache.get(item1)
        if subcache is None:
            return None
        return subcache.get(item2)

    def set(self, similarity:tuple[float, bool], item1:A, item2:A, environment1:StructureInfo.StructureInfo, environment2:StructureInfo.StructureInfo) -> tuple[float, bool]:
        environment_cache = self.cache[environment1, environment2]
        subcache = environment_cache.get(item1)
        if subcache is None:
            subcache = environment_cache[item1] = WeakKeyDictionary()
        subcache[item2] = similarity
        return similarity

    def clear(self, keep:Container[StructureInfo.StructureInfo]) -> None:
        '''
        Clears all environment caches that do not have both environments in `keep`.
        :keep: A Container of PrinterEnvironments to keep in the cache.
        '''
        removals:list[tuple[StructureInfo.StructureInfo, StructureInfo.StructureInfo]] = []
        for (environment1, environment2), environment_cache in self.cache.items():
            # environment_cache would have length 0 if all keys were garbage collected.
            if len(environment_cache) == 0 or environment1 not in removals and environment2 not in removals:
                removals.append((environment1, environment2))
        for removal_item in removals:
            self.cache.pop(removal_item)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} size {len(self.cache)}>"
