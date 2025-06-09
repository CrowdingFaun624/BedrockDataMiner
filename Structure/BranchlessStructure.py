from types import EllipsisType
from typing import Mapping, Sequence

from Structure.Container import Con, Don
from Structure.Difference import Diff
from Structure.PassthroughStructure import PassthroughStructure
from Structure.Structure import Structure
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Utilities.Exceptions import StructureTypeError
from Utilities.Trace import Trace

foo = False

class BranchlessStructure[D, BO, CO](PassthroughStructure[D, BO, CO]):

    __slots__ = (
        "structure",
        "this_types",
    )

    def link_branchless_structure(
        self,
        structure:Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None,
        this_types:tuple[type,...],
    ) -> None:
        self.structure = structure
        self.this_types = this_types

    def iter_structures(self) -> Sequence[Structure]:
        return (self.structure,) if self.structure is not None else ()

    def type_check_extra(self, data: Con[D], trace: Trace, environment: PrinterEnvironment) -> None:
        if not isinstance(data.data, self.this_types):
            trace.exception(StructureTypeError(self.this_types, type(data.data), "Data"))

    def get_structure(self, data: D, trace: Trace, environment: PrinterEnvironment) -> Structure[D, Con[D], Don[D], Don[D]|Diff[Don[D]], BO, CO]|None:
        return self.structure

    def diffize(self, data: Con[D], bundle: tuple[int, ...], trace: Trace, environment: ComparisonEnvironment) -> Mapping[tuple[int,...],Don[D]]|EllipsisType:
        with trace.enter(self, self.name, data):
            if self.structure is None:
                return {bundle: data.as_don(bundle)}
            else:
                return self.structure.diffize(data, bundle, trace, environment)
        return ...

    def compare(self, datas: tuple[tuple[int, Con[D]], ...], trace: Trace, environment: ComparisonEnvironment) -> tuple[Don[D]|Diff[Don[D]]|EllipsisType, bool, bool]:
        with trace.enter(self, self.name, datas):

            if self.structure is None:
                consecutive_similarities = self.get_consecutive_similarities(datas, trace, environment)
                return Diff(self.get_without_structure_comparison(consecutive_similarities), False), True, False

            else:
                comparison, any_changes, internal_changes = self.structure.compare(datas, trace, environment)

            if comparison is ...:
                # error has occurred in `structure.compare`
                return ..., False, False
            elif isinstance(comparison, Diff):
                return comparison, any_changes, internal_changes
            else:
                return Diff({tuple(branch for branch, _ in datas): comparison}, internal_changes), any_changes, internal_changes

        return ..., False, False
