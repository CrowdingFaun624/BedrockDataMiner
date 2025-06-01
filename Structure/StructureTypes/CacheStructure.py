from types import EllipsisType
from typing import Any, Callable, Mapping, Self, Sequence, cast

import Structure.BranchlessStructure as BranchlessStructure
import Structure.Container as Con
import Structure.DataPath as DataPath
import Structure.Delegate.Delegate as Delegate
import Structure.Difference as Diff
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTag as StructureTag
import Utilities.Trace as Trace


class CacheStructure[D, BO, BC, CO, CC](BranchlessStructure.BranchlessStructure[D, BO, CO]):

    __slots__ = (
        "cache_compare",
        "cache_containerize",
        "cache_diffize",
        "cache_get_referenced_files",
        "cache_get_similarity",
        "cache_get_tag_paths",
        "cache_normalize",
        "cache_print_branch",
        "cache_print_comparison",
        "cache_type_check",
        "delegate",
        "index",
        "removal_threshold",
    )

    any_delegate_works = True

    def link_cache_structure(
        self,
        delegate:Delegate.Delegate[Con.Con[D], Con.Don[D]|Diff.Diff[Con.Don[D]], Self, BO, BC, CO, CC]|None,
        removal_threshold:int,
    ) -> None:
        self.delegate = delegate
        self.removal_threshold = removal_threshold

        self.index:int = 0
        # when adding a new cache, make sure to add it to `all_caches`!
        self.cache_normalize:dict[int, tuple[D, int]] = {}
        self.cache_containerize:dict[int, tuple[Con.Con[D]|EllipsisType, int]] = {}
        self.cache_diffize:dict[int, tuple[Mapping[tuple[int, ...], Con.Don[D]] | EllipsisType, int]] = {}
        self.cache_type_check:dict[int, tuple[None, int]] = {}
        self.cache_get_tag_paths:dict[int, tuple[list[DataPath.DataPath], int]] = {}
        self.cache_get_referenced_files:dict[int, tuple[set[int], int]] = {}
        self.cache_compare:dict[int, tuple[tuple[Con.Don[D]|Diff.Diff[Con.Don[D]] | EllipsisType, bool, bool], int]] = {}
        self.cache_get_similarity:dict[int, tuple[tuple[float, bool], int]] = {}
        self.cache_print_branch:dict[int, tuple[Any, int]] = {}
        self.cache_print_comparison:dict[int, tuple[Any, int]] = {}

    @property
    def all_caches(self) -> tuple[dict[int,tuple[Any,int]],...]:
        return (
            self.cache_normalize,
            self.cache_containerize,
            self.cache_diffize,
            self.cache_type_check,
            self.cache_get_tag_paths,
            self.cache_get_referenced_files,
            self.cache_compare,
            self.cache_get_similarity,
            self.cache_print_branch,
            self.cache_print_comparison,
        )

    def get_structure(self, data:D, trace: Trace.Trace, environment:StructureEnvironment.PrinterEnvironment) -> Structure.Structure[D, Con.Con[D], Con.Don[D], Con.Don[D]|Diff.Diff[Con.Don[D]], BO, CO]|None:
        return self.structure

    def get_structure_chain_end(self, data: Con.Con[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Structure.Structure | None:
        # needs to interrupt chain in order to cache.
        return self

    def iter_structures(self) -> Sequence[Structure.Structure]:
        return (self.structure,) if self.structure is not None else ()

    def cache_function[A, B](
        self,
        cache:dict[int, tuple[B, int]],
        hash_function:Callable[[],int],
        cached_function:Callable[[], A],
        store_function:Callable[[A], B],
        retrieve_function:Callable[[B], A],
        environment:StructureEnvironment.StructureEnvironment,
    ) -> A:
        if not environment.should_cache:
            return cached_function()
        data_hash = hash_function()
        if (cached_output := cache.pop(data_hash, (..., self.index))[0]) is ...:
            output = cached_function()
            cache[data_hash] = (store_function(output), self.index)
            return output
        else:
            cache[data_hash] = (cached_output, self.index)
            return retrieve_function(cached_output)

    def delegate_store_branch(self, output:BO, trace:Trace.Trace, environment:StructureEnvironment.PrinterEnvironment) -> BC:
        if self.delegate is not None:
            return self.delegate.cache_store_branch(output, trace, environment)
        elif environment.default_delegate is not None:
            return environment.default_delegate.cache_store_branch(output, trace, environment)
        else:
            return cast(BC, output)

    def delegate_retrieve_branch(self, output:BC, trace:Trace.Trace, environment:StructureEnvironment.PrinterEnvironment) -> BO:
        if self.delegate is not None:
            return self.delegate.cache_retrieve_branch(output, trace, environment)
        elif environment.default_delegate is not None:
            return environment.default_delegate.cache_retrieve_branch(output, trace, environment)
        else:
            return cast(BO, output)

    def delegate_store_comparison(self, output:CO, trace:Trace.Trace, environment:StructureEnvironment.ComparisonEnvironment) -> CC:
        if self.delegate is not None:
            return self.delegate.cache_store_comparison(output, trace, environment)
        elif environment.default_delegate is not None:
            return environment.default_delegate.cache_store_comparison(output, trace, environment)
        else:
            return cast(CC, output)

    def delegate_retrieve_comparison(self, output:CC, trace:Trace.Trace, environment:StructureEnvironment.ComparisonEnvironment) -> CO:
        if self.delegate is not None:
            return self.delegate.cache_retrieve_comparison(output, trace, environment)
        elif environment.default_delegate is not None:
            return environment.default_delegate.cache_retrieve_comparison(output, trace, environment)
        else:
            return cast(CO, output)

    def normalize(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> D | EllipsisType:
        with trace.enter(self, self.name, data):
            hash_function = lambda: environment.domain.type_stuff.hash_data(data)
            self_super = super()
            return self.cache_function(self.cache_normalize, hash_function, lambda: self_super.normalize(data, trace, environment), lambda output: (output if output is not ... else data), lambda output: output, environment.structure_environment)
        return ...

    def containerize(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Con.Con[D] | EllipsisType:
        with trace.enter(self, self.name, data):
            hash_function = lambda: environment.domain.type_stuff.hash_data(data)
            self_super = super()
            return self.cache_function(self.cache_containerize, hash_function, lambda: self_super.containerize(data, trace, environment), lambda a: a, lambda a: a, environment.structure_environment)
        return ...

    def diffize(self, data: Con.Con[D], bundle: tuple[int, ...], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> Mapping[tuple[int, ...], Con.Don[D]] | EllipsisType:
        with trace.enter(self, self.name, data):
            self_super = super()
            return self.cache_function(self.cache_diffize, lambda: hash((data, bundle)), lambda: self_super.diffize(data, bundle, trace, environment), lambda a: a, lambda a: a, environment.structure_environment)
        return ...

    def type_check(self, data: Con.Con[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> None:
        with trace.enter(self, self.name, data):
            self_super = super()
            return self.cache_function(self.cache_type_check, lambda: hash(data), lambda: self_super.type_check(data, trace, environment), lambda a: a, lambda a: a, environment.structure_environment)
        return None

    def get_tag_paths(self, data: Con.Con[D], tag: StructureTag.StructureTag, data_path: DataPath.DataPath, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Sequence[DataPath.DataPath]:
        with trace.enter(self, self.name, data):
            store_function:Callable[[Sequence[DataPath.DataPath]], list[DataPath.DataPath]] = lambda output: [data_path.copy() for data_path in output]
            self_super = super()
            return self.cache_function(self.cache_get_tag_paths, lambda: hash((data, tag, data_path)), lambda: self_super.get_tag_paths(data, tag, data_path, trace, environment), store_function, store_function, environment.structure_environment)
        return ()

    def get_referenced_files(self, data: Con.Con[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> set[int]:
        with trace.enter(self, self.name, data):
            self_super = super()
            return self.cache_function(self.cache_get_referenced_files, lambda: hash(data), lambda: self_super.get_referenced_files(data, trace, environment), lambda a: a, lambda a: a, environment.structure_environment)
        return set()

    def compare(self, datas: tuple[tuple[int, Con.Con[D]], ...], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[Con.Don[D]|Diff.Diff[Con.Don[D]] | EllipsisType, bool, bool]:
        with trace.enter(self, self.name, datas):
            self_super = super()
            return self.cache_function(self.cache_compare, lambda: hash(datas), lambda: self_super.compare(datas, trace, environment), lambda a: a, lambda a: a, environment[-1].structure_environment)
        return ..., False, False

    def get_similarity(self, data1: Con.Con[D], data2: Con.Con[D], branch1: int, branch2: int, trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[float, bool]:
        with trace.enter(self, self.name, (data1, data2)):
            hash_function = lambda: hash((data1, data2, branch1, branch2))
            self_super = super()
            return self.cache_function(self.cache_get_similarity, hash_function, lambda: self_super.get_similarity(data1, data2, branch1, branch2, trace, environment), lambda a: a, lambda a: a, environment[branch2].structure_environment)
        return 0.0, False

    def print_branch(self, data: Con.Con[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> BO|EllipsisType:
        with trace.enter(self, self.name, data):
            store_function = lambda output: self.delegate_store_branch(output, trace, environment)
            retrieve_function = lambda output: self.delegate_retrieve_branch(output, trace, environment)
            self_super = super()
            return self.cache_function(self.cache_print_branch, lambda: hash(data), lambda: self_super.print_branch(data, trace, environment), store_function, retrieve_function, environment.structure_environment)
        return ...

    def print_comparison(self, data: Con.Don[D] | Diff.Diff[Con.Don[D]], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> CO|EllipsisType:
        with trace.enter(self, self.name, data):
            store_function = lambda output: self.delegate_store_comparison(output, trace, environment)
            retrieve_function = lambda output: self.delegate_retrieve_comparison(output, trace, environment)
            self_super = super()
            return self.cache_function(self.cache_print_comparison, lambda: hash(data), lambda: self_super.print_comparison(data, trace, environment), store_function, retrieve_function, environment[-1].structure_environment)
        return ...

    def clear_old(self) -> None:
        # Because cache items are popped and then re-added, caches are sorted by time accessed.
        # We can stop iterating part way through because of this.
        for cache in self.all_caches:
            items_to_remove:list[int] = [] # cannot change size of dict while iterating.
            for data_hash, (cache_item, last_retreival_index) in cache.items():
                if self.index - last_retreival_index >= self.removal_threshold:
                    items_to_remove.append(data_hash)
                else:
                    break
            for data_hash in items_to_remove:
                del cache[data_hash]
        self.index += 1

    def clear_all(self) -> None:
        for cache in self.all_caches:
            cache.clear()
