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
from Structure.WithinContainer import WCon, WDon, wdon_from_container, wdon_wrap
from Utilities.Exceptions import InvalidStateError, StructureTypeError
from Utilities.Trace import Trace


class WithinStructure[A, B, BO, CO](Structure[A, WCon[A, Con[B]], WDon[A, Don[B], Con[B]], WDon[A, Don[B], Con[B]]|Diff[WDon[A, Don[B], Con[B]]], BO, CO]):
    """
    Calls a non-modifying function on data and passes that to its singular sub-Structure.
    """

    __slots__ = (
        "inner_type_list",
        "inner_types",
        "outer_type_list",
        "outer_types",
        "similarity_cache",
        "structure",
        "tag_list",
        "tags",
    )

    def link_within_structure(
        self,
        inner_types:types_type,
        outer_types:types_type,
        structure:Structure[B, Con[B], Don[B], Don[B]|Diff[Don[B]], BO, CO],
        tags:tags_type,
    ) -> None:
        self.inner_type_list = inner_types
        self.outer_type_list = outer_types
        self.structure = structure
        self.tag_list = tags

        self.similarity_cache:SimilarityCache[Con[A]] = SimilarityCache()

    def finalize_within_structure(self) -> None:
        self.inner_types = convert_types_to_tuple(self.inner_type_list)
        del self.inner_type_list
        self.outer_types = convert_types_to_tuple(self.outer_type_list)
        del self.outer_type_list
        self.tags = convert_tags_to_set(self.tag_list)
        del self.tag_list

    def get_similarity_caches(self) -> Sequence[SimilarityCache]:
        return (self.similarity_cache,)

    def get_substructure(self, data: WCon[A, Con[B]], trace: Trace, environment: PrinterEnvironment) -> tuple[Con[B], Structure[Any, Con[B], Any, Any, Any, Any]|None]:
        return data.insides, self.structure

    def get_insides(self, data:A, trace:Trace, environment:PrinterEnvironment) -> B|EllipsisType:
        """
        Function called once on the data during containerization.

        Should **NOT** modify its input
        """
        ...

    def containerize(self, data: A, trace: Trace, environment: PrinterEnvironment) -> WCon[A, Con[B]] | EllipsisType:
        with trace.enter(self, self.trace_name, data):
            if not isinstance(data, self.outer_types):
                trace.exception(StructureTypeError(self.outer_types, type(data), "Outer data"))
                return ...
            new_data = self.get_insides(data, trace, environment)
            if new_data is ...:
                return ...
            if not isinstance(new_data, self.inner_types):
                trace.exception(StructureTypeError(self.inner_types, type(new_data), "Inner data"))
                return ...
            subcontainer = self.structure.containerize(new_data, trace, environment)
            if subcontainer is ...:
                return ...
            return WCon(data, subcontainer)
        return ...

    def diffize(self, data: WCon[A, Con[B]], bundle: tuple[int, ...], trace: Trace, environment: ComparisonEnvironment) -> Mapping[tuple[int,...],WDon[A, Don[B], Con[B]]]|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            diffize_output = self.structure.diffize(data.insides, bundle, trace, environment)
            if diffize_output is ...:
                return ...
            return {subbundle: wdon_from_container({branch: data for branch in subbundle}, dontainer) for subbundle, dontainer in diffize_output.items()}
        return ...

    def type_check(self, data: WCon[A, Con[B]], trace: Trace, environment: PrinterEnvironment) -> None:
        with trace.enter(self, self.trace_name, data):
            if not isinstance(data.data, self.outer_types):
                trace.exception(StructureTypeError(self.outer_types, type(data.data), "Outer data"))
        with trace.enter(self, self.trace_name, data.insides):
            if not isinstance(data.insides.data, self.inner_types):
                trace.exception(StructureTypeError(self.inner_types, type(data.insides.data), "Inner data"))
            self.structure.type_check(data.insides, trace, environment)

    def get_tag_paths(self, data: WCon[A, Con[B]], tag: StructureTag, data_path: DataPath, trace: Trace, environment: PrinterEnvironment) -> Sequence[DataPath]:
        with trace.enter(self, self.trace_name, data):
            if tag not in self.children_tags:
                return ()
            output:list[DataPath] = []
            if tag in self.tags:
                output.append(data_path.copy(...).embed(data.data))
            output.extend(self.structure.get_tag_paths(data.insides, tag, data_path, trace, environment))
            return output
        return ()

    def get_uses(self, data: WCon[A, Con[B]], usage_tracker: UsageTracker, parent_use:Use|None, trace: Trace, environment: PrinterEnvironment) -> OrderedSet[Use]:
        if not usage_tracker.still_used(self): return OrderedSet(())
        with trace.enter(self, self.trace_name, data):
            output:OrderedSet[Use] = OrderedSet(())
            self_use = StructureUse(self, usage_tracker, parent_use)
            output.add(self_use)
            for outer_type in self.outer_types:
                if isinstance(data.data, outer_type):
                    output.add(TypeUse(outer_type, Region.outer_types, self_use, usage_tracker))
                    break
            else: raise StructureTypeError(self.outer_types, type(data.data), "Outer data")
            for inner_type in self.inner_types:
                if isinstance(data.insides.data, inner_type):
                    output.add(TypeUse(inner_type, Region.inner_types, self_use, usage_tracker))
                    break
            else: raise StructureTypeError(self.inner_types, type(data.insides.data), "Inner data")
            output.update(self.structure.get_uses(data.insides, usage_tracker, self_use if self.structure.is_inline else None, trace, environment))
            return output
        return OrderedSet(())

    def get_all_uses(self, memo:set[Structure], parent_use:Use|None) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        memo.add(self)
        self_use = StructureUse(self, None, parent_use)
        output:OrderedSet[Use] = OrderedSet((self_use,))
        for outer_type in self.outer_types:
            output.add(TypeUse(outer_type, Region.outer_types, self_use, None))
        for inner_type in self.inner_types:
            output.add(TypeUse(inner_type, Region.inner_types, self_use, None))
        output.update(self.structure.get_all_uses(memo, self_use if self.structure.is_inline else None))
        return output

    def compare(self, datas: tuple[tuple[int, WCon[A, Con[B]]], ...], trace: Trace, environment: ComparisonEnvironment) -> tuple[WDon[A, Don[B], Con[B]]|Diff[WDon[A, Don[B], Con[B]]]|EllipsisType, bool, bool]:
        with trace.enter(self, self.trace_name, datas):

            insides_data = tuple((branch, data.insides) for branch, data in datas)
            comparison, any_changes, internal_changes = self.structure.compare(insides_data, trace, environment)
            if comparison is ...:
                # error has occurred in `structure.compare`
                return ..., False, False
            datas_mapping = {branch: data for branch, data in datas}
            return wdon_wrap(comparison, datas_mapping), any_changes, internal_changes

        return ..., False, False

    def get_comparison_insides(self, data:WDon[A, Don[B], Con[B]]|Diff[WDon[A, Don[B], Con[B]]]) -> Don[B]|Diff[Don[B]]:
        if isinstance(data, Diff):
            return Diff({bundle: item.insides for bundle, item in data.items.items()}, data.contains_diffs)
        else:
            return data.insides

    def get_similarity(self, data1: WCon[A, Con[B]], data2: WCon[A, Con[B]], branch1: int, branch2: int, trace: Trace, environment:ComparisonEnvironment) -> tuple[float, bool]:
        with trace.enter(self, self.trace_name, (data1, data2)):
            if (output := self.similarity_cache.get(data1, data2, environment[branch1], environment[branch2])) is not None:
                return output
            return self.structure.get_similarity(data1.insides, data2.insides, branch1, branch2, trace, environment)
        return 0.0, False

    def print_branch(self, data: WCon[A, Con[B]], trace: Trace, environment: PrinterEnvironment) -> BO|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            printer:Callable[[Con[B], Trace, PrinterEnvironment]]
            if self.structure is not None:
                printer = self.structure.print_branch
            else:
                raise InvalidStateError(self)
            return printer(data.insides, trace, environment)
        return ...

    def print_comparison(self, data: WDon[A, Don[B], Con[B]]|Diff[WDon[A, Don[B], Con[B]]], bundle:tuple[int,...], trace: Trace, environment: ComparisonEnvironment) -> CO|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            data_inside = self.get_comparison_insides(data)
            return self.get_comparison_printer(data, environment)(data_inside, bundle, trace, environment)
        return ...

    def get_comparison_printer(
        self,
        data: WDon[A, Don[B], Con[B]]|Diff[WDon[A, Don[B], Con[B]]],
        environment:ComparisonEnvironment,
    ) -> Callable[[Don[B]|Diff[Don[B]], tuple[int,...], Trace, ComparisonEnvironment], Any]:
        if isinstance(data, Don):
            return self.structure.print_comparison
        if isinstance(data, Diff) and data.length == 1:
            return self.structure.print_comparison
        raise InvalidStateError(self)
