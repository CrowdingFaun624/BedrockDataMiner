from itertools import pairwise
from types import EllipsisType
from typing import Any, Callable, Mapping, Self, Sequence

import Structure.DataPath as DataPath
import Structure.Delegate.Delegate as Delegate
import Structure.Difference as Diff
import Structure.Normalizer as Normalizer
import Structure.SimpleContainer as SCon
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Structure.StructureTag as StructureTag
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace


class PrimitiveStructure[D, BO, CO](Structure.Structure[D, SCon.SCon[D], SCon.SDon[D], Diff.Diff[SCon.SDon[D]], BO, CO]):

    __slots__ = (
        "delegate",
        "normalizers",
        "pre_normalized_types",
        "tags",
        "this_types",
    )

    def link_primitive_structure(
        self,
        delegate:Delegate.Delegate[SCon.SCon[D], Diff.Diff[SCon.SDon[D]], Self, BO, Any, CO, Any]|None,
        normalizers:Sequence[Normalizer.Normalizer],
        pre_normalized_types:tuple[type,...],
        tags:set[StructureTag.StructureTag],
        this_types:tuple[type,...],
    ) -> None:
        self.delegate = delegate
        self.normalizers = normalizers
        self.pre_normalized_types = pre_normalized_types
        self.tags = tags
        self.this_types = this_types

    def normalize(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> D | EllipsisType:
        with trace.enter(self, self.name, data):
            if not isinstance(data, self.pre_normalized_types):
                trace.exception(Exceptions.StructureTypeError(self.pre_normalized_types, type(data), "Data", "(pre-normalized)"))
                return ...
            data, data_identity_changed = self.normalizer_pass(self.normalizers, data, trace, environment)
            return data if data_identity_changed else ...
        return ...

    def containerize(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> SCon.SCon[D] | EllipsisType:
        with trace.enter(self, self.name, data):
            return SCon.SCon(data, environment.domain)
        return ...

    def diffize(self, data: SCon.SCon[D], bundle: tuple[int, ...], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> Mapping[tuple[int, ...], SCon.SDon[D]] | EllipsisType:
        with trace.enter(self, self.name, data):
            return {bundle: data.as_don(bundle)}
        return ...

    def type_check(self, data: SCon.SCon[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> None:
        with trace.enter(self, self.name, data):
            if not isinstance(data, self.this_types):
                trace.exception(Exceptions.StructureTypeError(self.this_types, type(data), "Data"))

    def get_tag_paths(self, data: SCon.SCon[D], tag: StructureTag.StructureTag, data_path: DataPath.DataPath, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Sequence[DataPath.DataPath]:
        with trace.enter(self, self.name, data):
            if tag not in self.children_tags:
                return ()
            if tag in self.tags:
                return (data_path.copy(...).embed(data),)
        return ()

    def get_referenced_files(self, data: SCon.SCon[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> set[int]:
        return set()

    def compare(self, datas: tuple[tuple[int, SCon.SCon[D]], ...], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[Diff.Diff[SCon.SDon[D]] | EllipsisType, bool, bool]:
        with trace.enter(self, self.name, datas):
            bundles:dict[tuple[int,...], SCon.SDon[D]] = {}
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
            return Diff.Diff(bundles, False), any_changes, False # contains_diffs=False and third item is False because there are no substructures to provide Diffs.
        return ..., False, False

    def get_similarity(self, data1: SCon.SCon[D], data2: SCon.SCon[D], branch1: int, branch2: int, trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[float, bool]:
        with trace.enter(self, self.name, (data1, data2)):
            return float(is_similar := (data1 == data2)), is_similar
        return 0.0, False

    def print_branch(self, data: SCon.SCon[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> BO|EllipsisType:
        with trace.enter(self, self.name, data):
            printer:Callable[[SCon.SCon[D], Trace.Trace, StructureEnvironment.PrinterEnvironment], Any]
            if self.delegate is not None:
                printer = self.delegate.print_branch
            elif environment.default_delegate is not None:
                printer = environment.default_delegate.print_branch
            else:
                raise Exceptions.InvalidStateError(self)
            return printer(data, trace, environment)
        return ...

    def print_comparison(self, data: Diff.Diff[SCon.SDon[D]], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> CO|EllipsisType:
        with trace.enter(self, self.name, data):
            printer:Callable[[Diff.Diff[SCon.SDon[D]], Trace.Trace, StructureEnvironment.ComparisonEnvironment], Any]
            if self.delegate is not None:
                printer = self.delegate.print_comparison
            elif environment.default_delegate is not None:
                printer = environment.default_delegate.print_comparison
            else:
                raise Exceptions.InvalidStateError(self)
            return printer(data, trace, environment)
        return ...
