from types import EllipsisType
from typing import Mapping

import Structure.Container as Con
import Structure.Difference as Diff
import Structure.PassthroughStructure as PassthroughStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace

foo = False

class BranchlessStructure[D, BO, CO](PassthroughStructure.PassthroughStructure[D, BO, CO]):

    __slots__ = (
        "structure",
        "this_types",
    )

    def link_branchless_structure(
        self,
        structure:Structure.Structure[D, Con.Con[D], Con.Don[D], Con.Don[D]|Diff.Diff[Con.Don[D]], BO, CO]|None,
        this_types:tuple[type,...],
    ) -> None:
        self.structure = structure
        self.this_types = this_types

    def iter_structures(self) -> Structure.Sequence[Structure.Structure]:
        return (self.structure,) if self.structure is not None else ()

    def type_check_extra(self, data: Con.Con[D], trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> None:
        if not isinstance(data.data, self.this_types):
            trace.exception(Exceptions.StructureTypeError(self.this_types, type(data.data), "Data"))

    def get_structure(self, data: D, trace: Trace.Trace, environment: StructureEnvironment.PrinterEnvironment) -> Structure.Structure[D, Con.Con[D], Con.Don[D], Con.Don[D]|Diff.Diff[Con.Don[D]], BO, CO]|None:
        return self.structure

    def diffize(self, data: Con.Con[D], bundle: tuple[int, ...], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> Mapping[tuple[int,...],Con.Don[D]]|EllipsisType:
        with trace.enter(self, self.name, data):
            if self.structure is None:
                return {bundle: data.as_don(bundle)}
            else:
                return self.structure.diffize(data, bundle, trace, environment)
        return ...

    def compare(self, datas: tuple[tuple[int, Con.Con[D]], ...], trace: Trace.Trace, environment: StructureEnvironment.ComparisonEnvironment) -> tuple[Con.Don[D]|Diff.Diff[Con.Don[D]]|EllipsisType, bool, bool]:
        with trace.enter(self, self.name, datas):
            consecutive_similarities = self.get_consecutive_similarities(datas, trace, environment)

            if all(consecutive_similarity[4][1] for consecutive_similarity in consecutive_similarities): # if all datas are equal
                diffized_output = self.diffize(datas[0][1], tuple(branch for branch, _ in datas), trace, environment)
                return ... if diffized_output is ... else Diff.Diff(diffized_output, False), False, False

            elif self.structure is None:
                return Diff.Diff(self.get_without_structure_comparison(consecutive_similarities), False), True, False

            else:
                comparison, internal_changes, _ = self.structure.compare(datas, trace, environment)
            if comparison is ...:
                # error has occurred in `structure.compare`
                return ..., False, False
            elif isinstance(comparison, Diff.Diff):
                return comparison, True, internal_changes
            else:
                return Diff.Diff({tuple(branch for branch, _ in datas): comparison}, internal_changes), True, internal_changes

        return ..., False, False
