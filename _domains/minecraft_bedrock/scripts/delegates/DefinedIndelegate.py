from types import EllipsisType
from typing import Any, Iterable

from Component.ComponentFunctions import component_function
from Structure.Delegate.LineDelegate import LineDelegate, LineType
from Structure.Difference import Diff
from Structure.IterableContainer import ICon, IDon
from Structure.IterableStructure import IterableStructure
from Structure.SimpleContainer import SCon, SDon
from Structure.StructureEnvironment import ComparisonEnvironment, PrinterEnvironment
from Utilities.Trace import Trace


@component_function()
class DefinedInDelegate(LineDelegate[ICon[SCon[int], SCon[str], tuple[str,...]], IDon[Diff[SDon[int]], Diff[SDon[str]], tuple[str,...], SCon[int], SCon[str]], IterableStructure]):

    applies_to = (IterableStructure,)

    def __init__(self, structure: IterableStructure, keys: dict[str, Any]) -> None:
        super().__init__(structure, keys, "", True, False)

    def print_data(self, data:Iterable[str]) -> str:
        return f"({", ".join(data)})"

    def print_branch(self, data: ICon[SCon[int], SCon[str], tuple[str,...]], trace: Trace, environment: PrinterEnvironment) -> list[LineType] | EllipsisType:
        return [(0, self.print_data(item.data for item in data.values()))]

    def print_comparison(self, data: IDon[Diff[SDon[int]], Diff[SDon[str]], tuple[str,...], SCon[int], SCon[str]], bundle: tuple[int], trace: Trace, environment: ComparisonEnvironment) -> list[LineType] | EllipsisType:
        return [(0, " -> ".join(self.print_data(data.get_con(branch).data) for branch in data.iter_branches()))]
