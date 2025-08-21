from itertools import pairwise
from types import EllipsisType
from typing import Any, Callable, Mapping, Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.DataPath import DataPath
from Structure.Difference import Diff
from Structure.SimilarityCache import SimilarityCache
from Structure.SimpleContainer import SCon
from Structure.Structure import Structure, convert_tags_to_set, tags_type
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Structure.StructureTag import StructureTag
from Structure.Uses import StructureUse, UsageTracker, Use
from Utilities.Exceptions import InvalidStateError
from Utilities.Trace import Trace


class PassthroughStructure[D, BO, CO, K](Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]):
    """
    Passes data through by choosing a particular Structure.
    """

    __slots__ = (
        "similarity_cache",
        "tag_list",
        "tags",
    )

    def link_passthrough_structure(
        self,
        tags:tags_type,
    ) -> None:
        self.tag_list = tags

        self.similarity_cache:SimilarityCache[Con[D]] = SimilarityCache()

    def finalize_passthrough_structure(self) -> None:
        self.tags = convert_tags_to_set(self.tag_list)
        del self.tag_list

    def get_similarity_caches(self) -> Sequence[SimilarityCache]:
        return (self.similarity_cache,)

    def get_structure(self, data:D, trace:Trace, environment:PrinterEnvironment) -> tuple[Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None, K|EllipsisType]:
        """
        :returns: A Structure that can act on the same data as this Structure or None,
        and a key that represents this Structure.
        """
        ...

    def get_substructure(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> tuple[Con[D], Structure[Any, Con[D], Any, Any, Any, Any] | None]:
        return data, self.get_structure(data.data, trace, environment)[0]

    def containerize(self, data: D, trace: Trace, environment: PrinterEnvironment) -> Con[D] | EllipsisType:
        with trace.enter(self, self.trace_name, data):
            structure, key = self.get_structure(data, trace, environment)
            if structure is None:
                return SCon(data, environment.domain)
            else:
                with (trace.enter_noop() if key is ... else trace.enter_key2(key, data)):
                    return structure.containerize(data, trace, environment)
        return ...

    def diffize(self, data: Con[D], bundle: tuple[int, ...], trace: Trace, environment: ComparisonEnvironment) -> Mapping[tuple[int,...],Don[D]]|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            structures = [(branch, self.get_structure(data.data, trace, environment[branch])) for branch in bundle]
            structure_bundles:list[tuple[tuple[int,...], Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None, tuple[K,...]]] = []
            current_bundle:list[int] = []
            current_structure:Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None|EllipsisType = ...
            current_keys: list[K] = []
            for branch, (structure, key) in structures:
                if current_structure is ... or structure is current_structure:
                    current_bundle.append(branch)
                    if key is not ...:
                        current_keys.append(key)
                else:
                    structure_bundles.append((tuple(current_bundle), current_structure, tuple(current_keys)))
                    current_bundle = [branch]
                    current_keys = [key] if key is not ... else []
                current_structure = structure
            assert current_structure is not ...
            structure_bundles.append((tuple(current_bundle), current_structure, tuple(current_keys)))
            output:dict[tuple[int,...], Don[D]] = {}
            for local_bundle, structure, keys in structure_bundles:
                if structure is None:
                    output[local_bundle] = data.as_don(local_bundle)
                else:
                    diffize_output = ...
                    with (trace.enter_noop() if len(keys) == 0 else trace.enter_key2(keys, data)):
                        diffize_output = structure.diffize(data, local_bundle, trace, environment)
                    if diffize_output is ...:
                        continue
                    output.update(diffize_output)
            return output
        return ...

    def type_check(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> None:
        with trace.enter(self, self.trace_name, data):
            self.type_check_extra(data, trace, environment)
            structure, key = self.get_structure(data.data, trace, environment)
            if structure is not None:
                with (trace.enter_noop() if key is ... else trace.enter_key2(key, data)):
                    structure.type_check(data, trace, environment)

    def type_check_extra(self, data:Con[D], trace:Trace, environment:PrinterEnvironment) -> None:
        ...

    def get_tag_paths(self, data: Con[D], tag: StructureTag, data_path: DataPath, trace: Trace, environment: PrinterEnvironment) -> Sequence[DataPath]:
        with trace.enter(self, self.trace_name, data):
            if tag not in self.children_tags:
                return ()
            output:list[DataPath] = []
            if tag in self.tags:
                output.append(data_path.copy(...).embed(data.data))
            structure, key = self.get_structure(data.data, trace, environment)
            output.extend(self.get_tag_paths_extra(data, tag, data_path, trace, environment))
            if structure is not None:
                with (trace.enter_noop() if key is ... else trace.enter_key2(key, data)):
                    output.extend(structure.get_tag_paths(data, tag, data_path, trace, environment))
            return output
        return ()

    def get_tag_paths_extra(self, data:Con[D], tag:StructureTag, data_path:DataPath, trace:Trace, environment:PrinterEnvironment) -> Sequence[DataPath]:
        return ()

    def get_uses(self, data: Con[D], usage_tracker:UsageTracker, parent_use:Use|None, trace: Trace, environment: PrinterEnvironment) -> OrderedSet[Use]:
        if not usage_tracker.still_used(self): return OrderedSet(())
        with trace.enter(self, self.trace_name, data):
            self_use = StructureUse(self, usage_tracker, parent_use)
            output:OrderedSet[Use] = OrderedSet((self_use,))
            structure, key = self.get_structure(data.data, trace, environment)
            if structure is not None:
                with (trace.enter_noop() if key is ... else trace.enter_key2(key, data)):
                    output.update(structure.get_uses(data, usage_tracker, self_use if structure.is_inline else None, trace, environment))
            return output
        return OrderedSet(())

    def get_all_uses(self, memo:set[Structure], parent_use:Use|None) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        memo.add(self)
        return OrderedSet((StructureUse(self, None, parent_use),))

    def compare(self, datas: tuple[tuple[int, Con[D]], ...], trace: Trace, environment: ComparisonEnvironment) -> tuple[Don[D]|Diff[Don[D]]|EllipsisType, bool, bool]:
        with trace.enter(self, self.trace_name, datas):
            structures = {branch: (data, self.get_structure(data.data, trace, environment[branch])) for branch, data in datas}

            bundles:list[tuple[tuple[int,...], tuple[K,...]]] = []
            last_structure:Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None|EllipsisType = ...
            current_bundle:list[int] = []
            current_keys:list[K] = []
            for branch, (data, (structure, key)) in structures.items():
                if last_structure is ... or last_structure is structure:
                    current_bundle.append(branch)
                    if key is not ...:
                        current_keys.append(key)
                else:
                    bundles.append((tuple(current_bundle), tuple(current_keys)))
                    current_bundle = [branch]
                    current_keys = [key] if key is not ... else []
                last_structure = structure
            bundles.append((tuple(current_bundle), tuple(current_keys)))

            bundle_comparisons:dict[tuple[int,...],Don[D]] = {}
            any_changes:bool = False
            any_internal_changes:bool = False
            for bundle, keys in bundles:
                local_datas = tuple((branch, structures[branch][0]) for branch in bundle) # all structures in this bundle are the same anyway.
                _, (structure, _) = structures[bundle[0]]
                with (trace.enter_noop() if len(keys) == 0 else trace.enter_key2(keys, local_datas[0][1])):
                    consecutive_similarities = self.get_consecutive_similarities(local_datas, trace, environment)
                    if all(consecutive_similarity[4][1] for consecutive_similarity in consecutive_similarities): # if all datas are equal
                        diffize_output = self.diffize(local_datas[0][1], bundle, trace, environment)
                        if diffize_output is ...: # error
                            continue
                        bundle_comparisons.update(diffize_output)
                        continue
                    any_changes = True
                    if structure is None:
                        bundle_comparisons.update(self.get_without_structure_comparison(consecutive_similarities))
                        continue
                    comparison, internal_changes, _ = structure.compare(local_datas, trace, environment)
                    any_internal_changes = any_internal_changes or internal_changes
                    if comparison is ...:
                        # error has occurred in `structure.compare`
                        continue
                    elif isinstance(comparison, Diff):
                        bundle_comparisons.update(comparison.items)
                    else:
                        bundle_comparisons[bundle] = comparison

            return Diff(bundle_comparisons, any_internal_changes), any_changes, any_internal_changes
        return ..., False, False

    def get_consecutive_similarities(
        self,
        local_datas:tuple[tuple[int,Con[D]],...],
        trace:Trace,
        environment:ComparisonEnvironment,
    ) -> list[tuple[int, int, Con[D], Con[D], tuple[float, bool]]]:
        return [
            (
                branch1,
                branch2,
                data1,
                data2,
                self.get_similarity(data1, data2, branch1, branch2, trace, environment),
            )
            for (branch1, data1), (branch2, data2) in pairwise(local_datas)
        ]

    def get_without_structure_comparison(self, consecutive_similarities:list[tuple[int, int, Con[D], Con[D], tuple[float, bool]]]) -> dict[tuple[int,...], Don[D]]:
        bundles:dict[tuple[int,...], Don[D]] = {}
        current_bundle:list[int] = [consecutive_similarities[0][0]] # start with the first branch because it won't be added otherwise.
        for branch1, branch2, data1, data2, (_, identical) in consecutive_similarities:
            if identical:
                current_bundle.append(branch2)
            else:
                bundles[tuple(current_bundle)] = data1.as_don((branch1,)) # data1 is from old
                current_bundle = [branch2] # start off with the first branch with different data.
        bundles[tuple(current_bundle)] = data2.as_don((branch2,))
        return bundles

    def get_similarity(self, data1: Con[D], data2: Con[D], branch1: int, branch2: int, trace: Trace, environment:ComparisonEnvironment) -> tuple[float, bool]:
        with trace.enter(self, self.trace_name, (data1, data2)):
            if data1 == data2:
                return 1.0, True
            if (output := self.similarity_cache.get(data1, data2, (environment1 := environment[branch1]), (environment2 := environment[branch2]))) is not None:
                return output
            keys:list[K] = []
            structure1, key1 = self.get_structure(data1.data, trace, environment1)
            if key1 is not ...: keys.append(key1)
            if structure1 is None:
                return self.similarity_cache.set((float(is_similar := (data1 == data2)), is_similar), data1, data2, environment1, environment2)
            structure2, key2 = self.get_structure(data2.data, trace, environment2)
            if key2 is not ...: keys.append(key2)
            if structure1 is not structure2:
                return self.similarity_cache.set((float(is_similar := (data1 == data2)), is_similar), data1, data2, environment1, environment2)

            with (trace.enter_noop() if len(keys) == 0 else trace.enter_key2(tuple(keys), (data1, data2))):
                return self.similarity_cache.set(structure1.get_similarity(data1, data2, branch1, branch2, trace, environment), data1, data2, environment1, environment2)
        return 0.0, False

    def has_branch_printer(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> bool:
        structure, _ = self.get_structure(data.data, trace, environment)
        return structure is not None and structure.has_branch_printer(data, trace, environment)

    def has_comparison_printer(self, data: Don[D] | Diff[Don[D]], trace: Trace, environment: ComparisonEnvironment) -> bool:
        if isinstance(data, Don):
            structures = [self.get_structure(data.get_con(branch).data, trace, environment[branch])[0] for branch in data.iter_branches()]
            return len(structures) > 0 and structures[0] is not None and all(structure is structures[0] for structure in structures) and structures[0].has_comparison_printer(data, trace, environment)
        else: # isinstance(data, Diff)
            if data.length != 1: return False
            structures = [self.get_structure(data[branch].get_con(branch).data, trace, environment[branch])[0] for branch in range(data.branch_count)]
            return structures[0] is not None and all(structure is structures[0] for structure in structures) and structures[0].has_comparison_printer(data, trace, environment)

    def print_branch(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> BO|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            structure, key = self.get_structure(data.data, trace, environment)
            if structure is not None:
                with (trace.enter_noop() if key is ... else trace.enter_key2(key, data)):
                    return structure.print_branch(data, trace, environment)
            else:
                raise InvalidStateError(self)
        return ...

    def print_comparison(self, data: Don[D] | Diff[Don[D]], bundle:tuple[int,...], trace: Trace, environment: ComparisonEnvironment) -> CO|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            printer, keys = self.get_comparison_printer(data, trace, environment)
            with (trace.enter_noop() if len(keys) == 0 else trace.enter_key2(keys, data)):
                return printer(data, bundle, trace, environment)
        return ...

    def get_comparison_printer(
        self,
        data: Don[D] | Diff[Don[D]],
        trace: Trace,
        environment:ComparisonEnvironment,
    ) -> tuple[Callable[[Don[D]|Diff[Don[D]], tuple[int,...], Trace, ComparisonEnvironment], Any], tuple[K,...]]:
        if isinstance(data, Don):
            structure:Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None|EllipsisType = ...
            keys:list[K] = []
            for branch in data.iter_branches():
                new_structure, key = self.get_structure(data.get_con(branch).data, trace, environment[branch])
                if structure is ...:
                    structure = new_structure
                if key is not ...:
                    keys.append(key)
                elif new_structure is not structure:
                    break
            else: # if structures obtained from all branches are the same.
                if structure is not None and structure is not ...: # an error occurred.
                    return structure.print_comparison, tuple(keys)
        if isinstance(data, Diff) and data.length == 1:
            common_structure:Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|EllipsisType = ...
            keys:list[K] = []
            for branch in range(data.branch_count):
                structure, key = self.get_structure(data[branch].get_con(branch).data, trace, environment[branch])
                if key is not ...:
                    keys.append(key)
                if structure is None:
                    raise InvalidStateError(self)
                elif common_structure is ...:
                    common_structure = structure
                elif structure is common_structure:
                    pass
                else: # too many Structures
                    raise InvalidStateError(self)
            if common_structure is ...:
                raise InvalidStateError(self)
            return common_structure.print_comparison, tuple(keys)
        raise InvalidStateError(self)
