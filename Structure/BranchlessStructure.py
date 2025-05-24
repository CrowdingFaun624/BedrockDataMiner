import Structure.Container as Con
import Structure.Difference as Diff
import Structure.PassthroughStructure as PassthroughStructure
import Structure.Structure as Structure
import Structure.StructureEnvironment as StructureEnvironment
import Utilities.Exceptions as Exceptions
import Utilities.Trace as Trace


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
