import gc
import time
from itertools import chain
from math import ceil

import psutil

import Domain.Domain as Domain
import Structure.SimilarityCache as SimilarityCache
from Structure.Structure import Structure
from Structure.StructureTypes.CacheStructure import CacheStructure
from Structure.StructureTypes.FileStructure import FileStructure

DEBUG:bool = False
MINIMUM_ADJUSTMENT_TIME:float = 20.0
CACHE_ADJUSTMENT_START:float = 0.7 # memory proportion at which caches are limited.
CACHE_ADJUSTMENT_END:float = 0.90 # memory proportion at which all caches are disabled.
CACHE_ADJUSTMENT_THRESHOLD:float = 0.05 # difference in adjustment to trigger a change.
CACHE_CLEAR:float = 0.93
ACCESSOR_MEMORY_CONSTRAIN = 0.92
SERIALIZER_MEMORY_CONSTRAIN = 0.93

class MemoryUsage():

    __slots__ = (
        "cache_structures",
        "current_accessor_memory_constrained",
        "current_cache_setting",
        "current_caches_disabled",
        "current_serializer_memory_constrained",
        "domains",
        "last_adjustment_time",
        "similarity_caches",
    )

    def __init__(self) -> None:
        self.last_adjustment_time:float = 0
        self.domains:list[Domain.Domain] = []
        self.cache_structures:list[CacheStructure] = []
        self.similarity_caches:list[SimilarityCache.SimilarityCache] = []

        self.current_cache_setting:float = 1.0 # adjuster of removal_threshold
        self.current_caches_disabled:bool = False
        self.current_accessor_memory_constrained:bool = False
        self.current_serializer_memory_constrained:bool = False

    def add_domain(self, domain:"Domain.Domain") -> None:
        self.domains.append(domain)
        structure_set:set[Structure] = set()
        for dataminer_collection in domain.dataminer_collections.values():
            dataminer_collection.structure.get_descendants(structure_set)
        all_structures = sorted(structure_set, key=lambda structure: structure.full_name)
        self.cache_structures.extend(structure for structure in all_structures if isinstance(structure, CacheStructure))
        self.similarity_caches.extend(chain.from_iterable(structure.get_similarity_caches() for structure in all_structures))

    def get_memory_usage_proportion(self) -> float:
        '''
        Returns a float between 0 and 1.
        '''
        return psutil.virtual_memory().percent / 100

    def set_cache_setting(self, new_cache_setting:float, force:bool=False) -> None:
        if not force and abs(new_cache_setting - self.current_cache_setting) < CACHE_ADJUSTMENT_THRESHOLD:
            return
        if DEBUG:
            print(f"Setting cache_setting to {new_cache_setting}")
        self.current_cache_setting = new_cache_setting
        for cache_structure in self.cache_structures:
            cache_structure.removal_threshold = ceil(cache_structure.default_removal_threshold * new_cache_setting)
        SimilarityCache.removal_threshold = ceil(SimilarityCache.DEFAULT_REMOVAL_THRESHOLD * new_cache_setting)

    def set_caches_disabled(self, disabled:bool) -> None:
        if disabled is self.current_caches_disabled:
            return
        self.current_caches_disabled = disabled
        for cache_structure in self.cache_structures:
            cache_structure.disabled = disabled
        if DEBUG:
            print(f"Setting caches_disabled to {disabled}")
        SimilarityCache.disabled = disabled
        if disabled:
            for cache_structure in self.cache_structures:
                cache_structure.clear_all()
            for similarity_cache in self.similarity_caches:
                similarity_cache.clear_all()

    def set_accessor_memory_constrain(self, enabled:bool) -> None:
        if enabled is self.current_accessor_memory_constrained:
            return
        if DEBUG:
            print(f"Setting accessor_memory_constrained to {enabled}")
        self.current_accessor_memory_constrained = enabled
        for domain in self.domains:
            for version in domain.versions.values():
                version.set_constrained_accessor_memory(enabled)

    def set_serializer_memory_constrain(self, enabled:bool) -> None:
        if enabled is self.current_serializer_memory_constrained:
            return
        if DEBUG:
            print(f"Setting serializer_memory_constrained to {enabled}")
        self.current_serializer_memory_constrained = enabled
        for domain in self.domains:
            for serializer in domain.serializers.values():
                if enabled:
                    serializer.memory_constrain()
                else:
                    serializer.memory_constrained = False

    def adjust(self) -> None:
        current_time = time.time()
        if current_time - self.last_adjustment_time < MINIMUM_ADJUSTMENT_TIME:
            return
        self.last_adjustment_time = current_time
        memory_proportion:float = self.get_memory_usage_proportion()
        if memory_proportion >= CACHE_ADJUSTMENT_END:
            new_cache_setting = 0.0
        elif memory_proportion >= CACHE_ADJUSTMENT_START:
            new_cache_setting = (memory_proportion - CACHE_ADJUSTMENT_END) / (CACHE_ADJUSTMENT_START - CACHE_ADJUSTMENT_END)
        else:
            new_cache_setting = 1.0
        self.set_cache_setting(new_cache_setting)
        self.set_caches_disabled(memory_proportion >= CACHE_CLEAR)
        self.set_accessor_memory_constrain(memory_proportion >= ACCESSOR_MEMORY_CONSTRAIN)
        self.set_serializer_memory_constrain(memory_proportion >= SERIALIZER_MEMORY_CONSTRAIN)
        gc.collect()

    def reset(self) -> None:
        self.set_cache_setting(1.0, force=True)
        self.set_caches_disabled(False)
        self.set_accessor_memory_constrain(False)

memory_usage = MemoryUsage()
memory_usage = MemoryUsage()
