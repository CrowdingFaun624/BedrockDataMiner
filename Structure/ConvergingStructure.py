from functools import reduce
from itertools import pairwise
from types import EllipsisType
from typing import Any, Callable, Mapping, Sequence

from ordered_set import OrderedSet

from Structure.Container import Con, Don
from Structure.DataPath import DataPath
from Structure.Difference import Diff
from Structure.SimilarityCache import SimilarityCache
from Structure.Structure import (
    Structure,
    convert_tags_to_set,
    convert_types_to_tuple,
    tags_type,
    types_type,
)
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Structure.StructureTag import StructureTag
from Structure.Uses import Region, StructureUse, TypeUse, UsageTracker, Use
from Structure.WithinContainer import WCon, WDon, wdon_wrap
from Utilities.Exceptions import (
    ConvergingStructureDepthError,
    ConvergingStructureEndError,
    InvalidStateError,
    StructureTypeError,
)
from Utilities.Trace import Trace


class ConvergingStructure[A, B, BO, CO](Structure[A, Con[A], Don[A], Don[A]|Diff[Don[A]], BO, CO]):
    """
    Contains a Structure that may branch out and converge again at a single Structure.
    """

    __slots__ = (
        "end_structure",
        "similarity_cache",
        "structure",
        "tag_list",
        "tags",
        "this_type_list",
        "this_types",
        "within_structure_depth",
    )

    def link_converging_structure(
        self,
        end_structure:Structure[B, Con[B], Don[B], Don[B]|Diff[Don[B]], BO, CO]|None,
        structure:Structure[A, Con[A], Don[A], Don[A]|Diff[Don[A]], BO, CO],
        tags:tags_type,
        this_types:types_type,
        within_structure_depth:int, # how many WithinStructures are in the chain until `end_structure`.
    ) -> None:
        self.end_structure = end_structure
        self.structure = structure
        self.tag_list = tags
        self.this_type_list = this_types
        self.within_structure_depth = within_structure_depth

        self.similarity_cache:SimilarityCache[Con[A]] = SimilarityCache()

    def finalize_converging_structure(self) -> None:
        self.tags = convert_tags_to_set(self.tag_list)
        del self.tag_list
        self.this_types = convert_types_to_tuple(self.this_type_list)
        del self.this_type_list

    def get_similarity_caches(self) -> Sequence[SimilarityCache]:
        return (self.similarity_cache,)

    def insides(self, data:Con[A]) -> Con[B]:
        insides_function:Callable[[WCon],Con] = lambda data: data.insides
        return reduce(lambda start, insides_func: insides_func(start), [insides_function] * self.within_structure_depth, data) # type: ignore

    def insides_comparison(self, data:Don[A]|Diff[Don[A]]) -> Don[B]|Diff[Don[B]]:
        insides_function:Callable[[WDon],Don] = lambda data: data.insides
        if isinstance(data, Diff):
            return Diff({bundle: reduce(lambda start, insides_func: insides_func(start), [insides_function] * self.within_structure_depth, item) for bundle, item in data.items.items()}, data.contains_diffs) # type: ignore
        else:
            return reduce(lambda start, insides_func: insides_func(start), [insides_function] * self.within_structure_depth, data) # type: ignore

    def insides_detailed(self, data:Con[A]) -> Sequence[Con[B]]:
        """
        Returns a sequence of unique Containers. The next one is immediately contained by the previous. Includes the argument.
        """
        output:list[Con[B]] = []
        subdata:WCon = data # type: ignore # if it isn't a WCon, then within_structure_depth must be 0.
        for _ in range(self.within_structure_depth):
            output.append(subdata)
            subdata = subdata.insides
        output.append(subdata)
        return output

    def containerize(self, data: A, trace: Trace, environment: PrinterEnvironment) -> Con[A] | EllipsisType:
        with trace.enter(self, self.trace_name, data):
            return self.structure.containerize(data, trace, environment)
        return ...

    def diffize(self, data: Con[A], bundle: tuple[int, ...], trace: Trace, environment: ComparisonEnvironment) -> Mapping[tuple[int,...],Don[A]]|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            return self.structure.diffize(data, bundle, trace, environment)
        return ...

    def type_check(self, data: Con[A], trace: Trace, environment: PrinterEnvironment) -> None:
        with trace.enter(self, self.trace_name, data):
            if not isinstance(data.data, self.this_types):
                trace.exception(StructureTypeError(self.this_types, type(data.data), "Data"))
            self.structure.type_check(data, trace, environment)

            # check that the ending Structure for this data really is what the user says it is.
            subdata:Con = data
            insides:int = 0
            structure:Structure|None = self.structure
            while True:
                if structure is None or structure is self.end_structure: # we check for it being the end structure because the user may choose to break it early due to inheritance etc.
                    break
                next_subdata, substructure = structure.get_substructure(subdata, trace, environment)
                if next_subdata is not subdata:
                    insides += 1
                    subdata = next_subdata
                if substructure is ...: # only happens if it's not a PassthroughStructure or WithinStructure, in which case the previously yielded Structure is the last one.
                    break
                structure = substructure
            if structure is not self.end_structure:
                trace.exception(ConvergingStructureEndError(self.end_structure, structure))
            if insides != self.within_structure_depth:
                trace.exception(ConvergingStructureDepthError(self.within_structure_depth, insides))

    def get_tag_paths(self, data: Con[A], tag: StructureTag, data_path: DataPath, trace: Trace, environment: PrinterEnvironment) -> Sequence[DataPath]:
        with trace.enter(self, self.trace_name, data):
            if tag not in self.children_tags:
                return ()
            output:list[DataPath] = []
            if tag in self.tags:
                output.append(data_path.copy(...).embed(data.data))
            output.extend(self.structure.get_tag_paths(data, tag, data_path, trace, environment))
            return output
        return ()

    def get_uses(self, data: Con[A], usage_tracker: UsageTracker, parent_use:Use|None, trace: Trace, environment: PrinterEnvironment) -> OrderedSet[Use]:
        if not usage_tracker.still_used(self): return OrderedSet(())
        with trace.enter(self, self.trace_name, data):
            output:OrderedSet[Use] = OrderedSet(())
            self_use = StructureUse(self, usage_tracker, parent_use)
            output.add(self_use)
            for this_type in self.this_types:
                if isinstance(data.data, this_type):
                    output.add(TypeUse(this_type, Region.outer_types, self_use, usage_tracker))
                    break
            else: raise StructureTypeError(self.this_types, type(data.data), "Data")
            output.update(self.structure.get_uses(data, usage_tracker, self_use if self.structure.is_inline else None, trace, environment))
            return output
        return OrderedSet(())

    def get_all_uses(self, memo:set[Structure], parent_use:Use|None) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        memo.add(self)
        self_use = StructureUse(self, None, parent_use)
        output:OrderedSet[Use] = OrderedSet((self_use,))
        for this_type in self.this_types:
            output.add(TypeUse(this_type, Region.this_types, self_use, None))
        output.update(self.structure.get_all_uses(memo, self_use if self.structure.is_inline else None))
        return output

    def compare(self, datas: tuple[tuple[int, Con[A]], ...], trace: Trace, environment: ComparisonEnvironment) -> tuple[Don[A]|Diff[Don[A]]|EllipsisType, bool, bool]:
        with trace.enter(self, self.trace_name, datas):

            detailed_data = tuple((branch, self.insides_detailed(data)) for branch, data in datas)
            insides_data = tuple((branch, data[-1]) for branch, data in detailed_data)
            if self.end_structure is None:
                bundles:dict[tuple[int,...], Don[B]] = {}
                current_bundle:list[int] = [insides_data[0][0]] # start with the first branch because it won't be added otherwise.
                for (branch1, data1), (branch2, data2) in pairwise(insides_data):
                    if data1 == data2:
                        current_bundle.append(branch2)
                    else:
                        bundles[tuple(current_bundle)] = data1.as_don((branch1,)) # data1 is from old
                        current_bundle = [branch2] # start off with the first branch with different data.
                bundles[tuple(current_bundle)] = data2.as_don((branch2,))
                comparison, any_changes, internal_changes = Diff(bundles, False), len(bundles) > 1, False
            else:
                comparison, any_changes, internal_changes = self.end_structure.compare(insides_data, trace, environment)
            if comparison is ...:
                # error has occurred in `structure.compare`
                return ..., False, False
            else:
                branch:int
                containers:Sequence[Con[B]]
                layered_data:list[dict[int,Con[B]]] = [{} for _ in detailed_data]
                for branch, containers in detailed_data:
                    for item, container in zip(layered_data, containers, strict=True):
                        item[branch] = container
                layered_data.pop() # do not need the last layer; it is filled with not-WCons
                for layer in reversed(layered_data): # shallowest data first
                    comparison = wdon_wrap(comparison, layer) # type: ignore
                new_comparison:Don[A]|Diff[Don[A]] = comparison # type: ignore
            return new_comparison, any_changes, internal_changes

        return ..., False, False

    def get_similarity(self, data1:Con[A], data2: Con[A], branch1: int, branch2: int, trace: Trace, environment:ComparisonEnvironment) -> tuple[float, bool]:
        with trace.enter(self, self.trace_name, (data1, data2)):
            if (output := self.similarity_cache.get(data1, data2, environment[branch1], environment[branch2])) is not None:
                return output
            inside_data1 = self.insides(data1)
            inside_data2 = self.insides(data2)
            if self.end_structure is None:
                return float(is_similar := (inside_data1 == inside_data2)), is_similar
            return self.end_structure.get_similarity(inside_data1, inside_data2, branch1, branch2, trace, environment)
        return 0.0, False

    def has_branch_printer(self, data: Con[A], trace: Trace, environment: PrinterEnvironment) -> bool:
        return True

    def has_comparison_printer(self, data: Don[A] | Diff[Don[A]], trace: Trace, environment: ComparisonEnvironment) -> bool:
        return self.end_structure is not None

    def print_branch(self, data: Con[A], trace: Trace, environment: PrinterEnvironment) -> BO|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            return self.structure.print_branch(data, trace, environment)
        return ...

    def print_comparison(self, data: Don[A]|Diff[Don[A]], bundle:tuple[int,...], trace: Trace, environment: ComparisonEnvironment) -> CO|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            data_insides = self.insides_comparison(data)
            if self.end_structure is None: # no printer is available
                raise InvalidStateError(self)
            return self.end_structure.print_comparison(data_insides, bundle, trace, environment)
        return ...
