from itertools import pairwise
from types import EllipsisType
from typing import Any, Callable, Mapping, Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.DataPath import DataPath
from Structure.Difference import Diff
from Structure.Normalizer import Normalizer
from Structure.SimilarityCache import SimilarityCache
from Structure.Structure import Structure
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Structure.StructureTag import StructureTag
from Structure.Uses import StructureUse, UsageTracker, Use
from Utilities.Exceptions import InvalidStateError
from Utilities.Trace import Trace


class AbstractPassthroughStructure[C, D, BO, CO](Structure[C, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]):
    '''
    Passes data through by choosing a particular Structure.
    '''

    __slots__ = (
        "normalizers",
        "post_normalizers",
        "pre_normalized_types",
        "similarity_cache",
        "tags",
    )

    def link_passthrough_structure(
        self,
        normalizers:Sequence[Normalizer],
        post_normalizers:Sequence[Normalizer],
        pre_normalized_types:tuple[type,...],
        tags:set[StructureTag],
    ) -> None:
        self.normalizers = normalizers
        self.post_normalizers = post_normalizers
        self.pre_normalized_types = pre_normalized_types
        self.tags = tags

        self.similarity_cache:SimilarityCache[Con[D]] = SimilarityCache()

    def get_similarity_caches(self) -> Sequence[SimilarityCache]:
        return (self.similarity_cache,)

    def get_structure(self, data:D, trace:Trace, environment:PrinterEnvironment) -> Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None:
        '''
        Returns a Structure that can act on the same data as this Structure or None.
        '''
        ...

    def get_structure_chain_end(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> Structure|None:
        with trace.enter(self, self.trace_name, data):
            structure = self.get_structure(data.data, trace, environment)
            return structure.get_structure_chain_end(data, trace, environment) if structure is not None else None

    def get_substructure_chain_end(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> Structure|None:
        substructure = self.get_structure(data.data, trace, environment)
        if substructure is None:
            return None
        else:
            return substructure.get_structure_chain_end(data, trace, environment)

    def diffize(self, data: Con[D], bundle: tuple[int, ...], trace: Trace, environment: ComparisonEnvironment) -> Mapping[tuple[int,...],Don[D]]|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            structures = [(branch, self.get_structure(data.data, trace, environment[branch])) for branch in bundle]
            structure_bundles:list[tuple[tuple[int,...], Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None]] = []
            current_bundle:list[int] = []
            current_structure:Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None|EllipsisType = ...
            for branch, structure in structures:
                if current_structure is ... or structure is current_structure:
                    current_bundle.append(branch)
                else:
                    structure_bundles.append((tuple(current_bundle), current_structure))
                    current_bundle = [branch]
                current_structure = structure
            assert current_structure is not ...
            structure_bundles.append((tuple(current_bundle), current_structure))
            output:dict[tuple[int,...], Don[D]] = {}
            for local_bundle, structure in structure_bundles:
                if structure is None:
                    output[local_bundle] = data.as_don(local_bundle)
                else:
                    diffize_output = structure.diffize(data, local_bundle, trace, environment)
                    if diffize_output is ...:
                        continue
                    output.update(diffize_output)
            return output
        return ...

    def type_check(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> None:
        with trace.enter(self, self.trace_name, data):
            self.type_check_extra(data, trace, environment)
            structure = self.get_structure(data.data, trace, environment)
            if structure is not None:
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
            structure = self.get_structure(data.data, trace, environment)
            output.extend(self.get_tag_paths_extra(data, tag, data_path, trace, environment))
            if structure is not None:
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
            structure = self.get_structure(data.data, trace, environment)
            if structure is not None:
                output.update(structure.get_uses(data, usage_tracker, self_use if structure.is_inline else None, trace, environment))
            return output
        return OrderedSet(())

    def get_all_uses(self, memo:set[Structure], parent_use:Use|None) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        memo.add(self)
        return OrderedSet((StructureUse(self, None, parent_use),))

    def compare(self, datas: tuple[tuple[int, Con[D]], ...], trace: Trace, environment: ComparisonEnvironment) -> tuple[Don[D]|Diff[Don[D]]|EllipsisType, bool, bool]:
        with trace.enter(self, self.trace_name, datas):
            structures = {branch: (data, self.get_substructure_chain_end(data, trace, environment[branch])) for branch, data in datas}

            bundles:list[tuple[int,...]] = []
            last_structure:Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None|EllipsisType = ...
            current_bundle:list[int] = []
            for branch, (data, structure) in structures.items():
                if last_structure is ... or last_structure is structure:
                    current_bundle.append(branch)
                else:
                    bundles.append(tuple(current_bundle))
                    current_bundle = [branch]
                last_structure = structure
            bundles.append(tuple(current_bundle))

            bundle_comparisons:dict[tuple[int,...],Don[D]] = {}
            any_changes:bool = False
            any_internal_changes:bool = False
            for bundle in bundles:
                local_datas = tuple((branch, structures[branch][0]) for branch in bundle) # all structures in this bundle are the same anyway.
                structure = structures[bundle[0]][1]
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
            if (output := self.similarity_cache.get(data1, data2, (environment1 := environment[branch1]).structure_info, (environment2 := environment[branch2]).structure_info)) is not None:
                return output
            structure1 = self.get_substructure_chain_end(data1, trace, environment1)
            if structure1 is None:
                return self.similarity_cache.set((float(is_similar := (data1 == data2)), is_similar), data1, data2, environment1.structure_info, environment2.structure_info)
            structure2 = self.get_substructure_chain_end(data2, trace, environment2)
            if structure1 is structure2:
                return self.similarity_cache.set(structure1.get_similarity(data1, data2, branch1, branch2, trace, environment), data1, data2, environment1.structure_info, environment2.structure_info)
            else:
                return self.similarity_cache.set((float(is_similar := (data1 == data2)), is_similar), data1, data2, environment1.structure_info, environment2.structure_info)
        return 0.0, False

    def print_branch(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> BO|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            structure = self.get_structure(data.data, trace, environment)
            printer:Callable[[Con[D], Trace, PrinterEnvironment]]
            if structure is not None:
                printer = structure.print_branch
            elif environment.default_delegate is not None:
                printer = environment.default_delegate.print_branch
            else:
                raise InvalidStateError(self)
            return printer(data, trace, environment)
        return ...

    def print_comparison(self, data: Don[D] | Diff[Don[D]], bundle:tuple[int,...], trace: Trace, environment: ComparisonEnvironment) -> CO|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            return self.get_comparison_printer(data, trace, environment)(data, bundle, trace, environment)
        return ...

    def get_comparison_printer(
        self,
        data: Don[D] | Diff[Don[D]],
        trace: Trace,
        environment:ComparisonEnvironment,
    ) -> Callable[[Don[D]|Diff[Don[D]], tuple[int,...], Trace, ComparisonEnvironment], Any]:
        if isinstance(data, Don):
            structure:Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None|EllipsisType = ...
            for branch in data.iter_branches():
                new_structure = self.get_substructure_chain_end(data.get_con(branch), trace, environment[branch])
                if structure is ...:
                    structure = new_structure
                elif new_structure is not structure:
                    break
            else: # if structures obtained from all branches are the same.
                if structure is not None and structure is not ...: # an error occurred.
                    return structure.print_comparison
        if isinstance(data, Diff) and data.length == 1 and\
            len(set((structures := [self.get_substructure_chain_end(data[branch].get_con(branch), trace, environment[branch]) for branch in range(data.branch_count)]))) == 1 and structures[0] is not None:
            # if all structures are the same and not None.
            return structures[0].print_comparison
        if environment.default_delegate is not None:
            return environment.default_delegate.print_comparison
        raise InvalidStateError(self)
