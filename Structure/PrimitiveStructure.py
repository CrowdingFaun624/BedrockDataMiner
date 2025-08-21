from itertools import pairwise
from types import EllipsisType
from typing import Any, Callable, Mapping, Self, Sequence

from ordered_set import OrderedSet

from Structure.DataPath import DataPath
from Structure.Delegate.Delegate import Delegate, DelegateCreator
from Structure.Difference import Diff
from Structure.SimpleContainer import SCon, SDon
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
from Utilities.Exceptions import InvalidStateError, StructureTypeError
from Utilities.Trace import Trace


class PrimitiveStructure[D, BO, CO](Structure[D, SCon[D], SDon[D], Diff[SDon[D]], BO, CO]):

    __slots__ = (
        "delegate",
        "delegate_creator",
        "tag_list",
        "tags",
        "this_type_list",
        "this_types",
    )

    def link_primitive_structure(
        self,
        delegate:DelegateCreator[Delegate[SCon[D], Diff[SDon[D]], Self, BO, Any, CO, Any]]|None,
        tags:tags_type,
        this_types:types_type,
    ) -> None:
        self.delegate_creator = delegate
        self.tag_list = tags
        self.this_type_list = this_types

    def finalize_primitive_structure(self, trace:Trace) -> bool:
        self.tags = convert_tags_to_set(self.tag_list)
        del self.tag_list
        self.this_types = convert_types_to_tuple(self.this_type_list)
        del self.this_type_list
        self.delegate = None if self.delegate_creator is None else self.delegate_creator.create_delegate(self)
        del self.delegate_creator
        return False if self.delegate is None else self.delegate.finalize(self.domain, trace)

    def containerize(self, data: D, trace: Trace, environment: PrinterEnvironment) -> SCon[D] | EllipsisType:
        with trace.enter(self, self.trace_name, data):
            return SCon(data, environment.domain)
        return ...

    def diffize(self, data: SCon[D], bundle: tuple[int, ...], trace: Trace, environment: ComparisonEnvironment) -> Mapping[tuple[int, ...], SDon[D]] | EllipsisType:
        with trace.enter(self, self.trace_name, data):
            return {bundle: data.as_don(bundle)}
        return ...

    def type_check(self, data: SCon[D], trace: Trace, environment: PrinterEnvironment) -> None:
        with trace.enter(self, self.trace_name, data):
            if not isinstance(data.data, self.this_types):
                trace.exception(StructureTypeError(self.this_types, type(data.data), "Data"))

    def get_tag_paths(self, data: SCon[D], tag: StructureTag, data_path: DataPath, trace: Trace, environment: PrinterEnvironment) -> Sequence[DataPath]:
        with trace.enter(self, self.trace_name, data):
            if tag not in self.children_tags:
                return ()
            if tag in self.tags:
                return (data_path.copy(...).embed(data.data),)
        return ()

    def get_uses(self, data: SCon[D], usage_tracker:UsageTracker, parent_use:Use|None, trace: Trace, environment: PrinterEnvironment) -> OrderedSet[Use]:
        if not usage_tracker.still_used(self): return OrderedSet(())
        with trace.enter(self, self.trace_name, data):
            self_use = StructureUse(self, usage_tracker, parent_use)
            output:OrderedSet[Use] = OrderedSet((self_use,))
            for this_type in self.this_types:
                if isinstance(data.data, this_type):
                    output.add(TypeUse(this_type, Region.this_types, self_use, usage_tracker))
                    break
            else: raise StructureTypeError(self.this_types, type(data.data), "Data")
            return output
        return OrderedSet(())

    def get_all_uses(self, memo: set[Structure], parent_use:Use|None) -> OrderedSet[Use]:
        if self in memo: return OrderedSet(())
        self_use = StructureUse(self, None, parent_use)
        output:OrderedSet[Use] = OrderedSet((self_use,))
        for this_type in self.this_types:
            output.add(TypeUse(this_type, Region.this_types, self_use, None))
        return output

    def compare(self, datas: tuple[tuple[int, SCon[D]], ...], trace: Trace, environment: ComparisonEnvironment) -> tuple[Diff[SDon[D]] | EllipsisType, bool, bool]:
        with trace.enter(self, self.trace_name, datas):
            bundles:dict[tuple[int,...], SDon[D]] = {}
            any_changes:bool = False
            current_bundle:list[int] = [datas[0][0]] # start off with the first branch because it won't be added otherwise.
            for (branch1, data1), (branch2, data2) in pairwise(datas):
                _, identical = self.get_similarity(data1, data2, branch1, branch2, trace, environment)
                if identical:
                    current_bundle.append(branch2)
                else:
                    any_changes = True
                    current_bundle_tuple = tuple(current_bundle)
                    bundles[current_bundle_tuple] = data1.as_don(current_bundle_tuple) # data1 is from old
                    current_bundle = [branch2] # new bundle starts with first branch having new data.
            current_bundle_tuple = tuple(current_bundle)
            bundles[current_bundle_tuple] = data2.as_don(current_bundle_tuple)
            return Diff(bundles, False), any_changes, False # contains_diffs=False and third item is False because there are no substructures to provide Diffs.
        return ..., False, False

    def get_similarity(self, data1: SCon[D], data2: SCon[D], branch1: int, branch2: int, trace: Trace, environment: ComparisonEnvironment) -> tuple[float, bool]:
        with trace.enter(self, self.trace_name, (data1, data2)):
            return float(is_similar := (data1 == data2)), is_similar
        return 0.0, False

    def has_branch_printer(self, data: SCon[D], trace: Trace, environment: PrinterEnvironment) -> bool:
        return self.delegate is not None

    def has_comparison_printer(self, data: Diff[SDon[D]], trace: Trace, environment: ComparisonEnvironment) -> bool:
        return self.delegate is not None

    def print_branch(self, data: SCon[D], trace: Trace, environment: PrinterEnvironment) -> BO|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            printer:Callable[[SCon[D], Trace, PrinterEnvironment], Any]
            if self.delegate is not None:
                printer = self.delegate.print_branch
            else:
                raise InvalidStateError(self)
            return printer(data, trace, environment)
        return ...

    def print_comparison(self, data: Diff[SDon[D]], bundle:tuple[int,...], trace: Trace, environment: ComparisonEnvironment) -> CO|EllipsisType:
        with trace.enter(self, self.trace_name, data):
            printer:Callable[[Diff[SDon[D]], tuple[int,...], Trace, ComparisonEnvironment], Any]
            if self.delegate is not None:
                printer = self.delegate.print_comparison
            else:
                raise InvalidStateError(self)
            return printer(data, bundle, trace, environment)
        return ...
